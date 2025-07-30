#!/usr/bin/env python3
"""General functions for creating and managing nvim instances.

These functions interact with the pynvim API library directly. For the higher
level interface that is exposed in lvim, see NvimSession and NvimBroker.
"""

from __future__ import annotations

from contextlib import contextmanager, nullcontext
from getpass import getuser
from logging import Logger, getLogger
from os import getenv, getpid
from pathlib import Path
from socket import AF_INET, AF_INET6, AF_UNIX, SOCK_STREAM, socket
from tempfile import TemporaryDirectory, gettempdir
from time import sleep
from typing import Dict, Generator, Optional, cast

from click import secho
from invoke import run
from invoke.runners import Promise
from pynvim import Nvim, attach

logger: Logger = getLogger(__name__)

HEADER: str = "return string.format('Neovim v%s running %s [%s]', vim.version(), jit.version, _VERSION)"


# Create temp dir for storing lvim data and sockets
@contextmanager
def tmp_dir() -> Generator[Path, None, None]:
    """Create a temp dir for storing lvim data and sockets.

    The directory is not deleted on exit, as nvim itself manages the socket.

    Roughly follows nvim's implementation for finding a default path:
    https://github.com/neovim/neovim/blob/8b9500c886bdb72620e331d430e166ad7d9c12f8/src/nvim/fileio.c#L3261
    https://github.com/neovim/neovim/blob/8b9500c886bdb72620e331d430e166ad7d9c12f8/src/nvim/msgpack_rpc/server.c#L117

    Yields:
        tmp_dir: Path. Path to created temporary directory.
    """

    # Sanitize username for use in path "/" and "\\" to "_"
    user = getuser().replace("/", "_").replace("\\\\", "_")
    # /tmp/lvim.aemiller
    user_path = Path(gettempdir()) / f"lvim.{user}"

    logger.debug(f"Creating user temporary directory at {user_path}")
    user_path.mkdir(exist_ok=True)

    # /tmp/lvim.aemiller/tmpjvzah0uu
    with TemporaryDirectory(dir=user_path, delete=False) as tmp_dir:
        yield Path(tmp_dir)


@contextmanager
def tmp_socket() -> Generator[str, None, None]:
    """Get the path to use for the nvim server socket in the temp directory.

    This is provided to nvim as the --listen argument, which will then create
    the socket in the given path.

    Yields:
        socket_path: str. Path to where the nvim server will store the socket.
    """

    with tmp_dir() as tmp:
        # /tmp/lvim.aemiller/tmpjvzah0uu/nvim.737363.0
        socket_path = str(tmp / f"nvim.{getpid()}.0")

        logger.debug(f"listen auto: Using temporary socket path {socket_path}")
        yield socket_path


@contextmanager
def nvim_start(listen: str = "auto", clean: bool = False) -> Generator[str, None, None]:
    """Context manager for auto starting and stopping a nvim server instance.

    This will create a temporary directory and socket path, and then use it to
    run an instance of nvim --headless --listen '$SOCKET' in another thread.

    Once the process is started, the context will wait for the server to be
    connectable at the listen location before yielding.

    Finally, once the context edits, the server will be cleanly shut down using
    vim.quit() (which just runs :qa!) over RPC.

    Args:
        listen: str. Listen address or socket path. By default, this is "auto",
            which will automatically derive a unix socket path in the tmp dir.
        clean: bool. If True, nvim will be started with the --clean option, which
            skips all user config/sessions/shada.

    Yields:
        listen_path: str. Path to the unix socket or TCP address where the started
            nvim server is listening.
    """

    maybe_clean = "--clean " if clean else ""
    maybe_auto = "auto " if listen == "auto" else ""
    listen_ctx = tmp_socket() if listen == "auto" else nullcontext(enter_result=listen)
    nvim = None
    try:
        with listen_ctx as listen_path:
            logger.debug("Starting nvim listen server")
            cmd = f"/bin/env nvim {maybe_clean}--headless --listen '{listen_path}'"
            secho(f"{maybe_auto}starting nvim with: {cmd}")

            nvim = cast(Promise, run(cmd, asynchronous=True))

            if "/" in listen_path:
                # For sockets, wait until the socket exists before trying to connect
                socket_path = Path(listen_path)
                while not socket_path.is_socket():
                    sleep(0.1)

                # Now try connecting to the socket and continue when it goes through
                with socket(AF_UNIX, SOCK_STREAM) as sock:
                    sock.connect(listen_path)
            else:
                # For normal IP sockets, just wait until the connection works
                host, _, port = listen_path.rpartition(":")
                family = AF_INET if ":" not in host else AF_INET6
                with socket(family, SOCK_STREAM) as sock:
                    while True:
                        try:
                            sock.connect((host, int(port)))
                            break
                        except ConnectionRefusedError:
                            sleep(0.1)

            yield listen_path
    finally:
        try:
            secho(f"{maybe_auto}stopping nvim")
            with nvim_attach(listen_path) as vim:
                logger.debug("Issuing shutdown cmd :qa! to listen server")
                vim.quit()
        except (ConnectionRefusedError, FileNotFoundError):
            # Nothing listening there anymore
            pass

        logger.debug("Waiting for listen server to shutdown")
        nvim.join()


def tmux_environment() -> Dict[str, str]:
    """Retrieve the tmux "environment" for the session.

    This is all settings set via tmux set-environment ie:
    -DISPLAY
    -KRB5CCNAME
    NVIM=localhost:7861

    Gives:
    {"-DISPLAY": None, "-KRB5CCNAME": None, "NVIM": "localhost:7861"}

    This is preferred over reading the environment variables directly, as those
    are not updated for existing windows when set.

    Args:
        ctx: Context. Summoner context to use for tmux CLI.

    Returns:
        environment: Dict[str, str]. The tmux environment.
    """

    result = run("tmux show-environment", hide="both")
    if result is None:
        raise ValueError()
    else:
        env_out = result

    env_vars = {}
    for line in env_out.stdout.rstrip().split("\n"):
        env_split = line.rstrip().split("=", 1)

        if len(env_split) == 1:
            env_vars[env_split[0]] = None
        else:
            env_vars[env_split[0]] = env_split[1]

    return env_vars


def nvim_connection() -> Optional[str]:
    """Get the path to the NVIM connection from the local or tmux environment.

    If this is running in tmux, the value for $NVIM will be retrieved from the
    session local tmux environment by running tmux show-environment. This ensures
    the most up to date value set by a running nvim server itself.

    Connection is either a host/port ie localhost:7861 or a /path/to/a/socket.

    Returns:
        socket: str. Connection to nvim instance for this lvim (tmux) session.
    """

    if getenv("TMUX", None):
        # tmux set-environment doesn't push the change to existing windows, so
        # always grab it from tmux show-environment if available
        connection = tmux_environment().get("NVIM", None)
    else:
        # Otherwise fallback to the normal environment variable nvim sets
        connection = getenv("NVIM", None)

    return connection


def _embedded_pid(nvim: Nvim) -> int:
    """Get the process ID of an nvim instance started with --embed"""

    # This is the easiest way I could find the PID, it will probably break in
    # the future
    # vim.funcs.getpid()/vim.uv.getpid()/vim.uv.os_getpid() all just return the
    # ID of lvim, ppid works
    return nvim.exec_lua("return vim.uv.os_getppid()")


def show_header(nvim: Nvim, connection: str) -> None:
    """Display a header in the lvim REPL with PID and connection info.

    Args:
        nvim: Nvim. Connected Nvim API client.
        connection: str. Connection used by the API client.
    """

    if connection == "embedded" or connection == "embedded_clean":
        conn = f"Embedded PID {_embedded_pid(nvim)}"
    elif "/" in connection:
        # TODO: This only works for --listen with unix sockets/auto, and is hacky
        if "lvim" in connection:
            conn = f"Listen {connection}"
        else:
            conn = f"Socket {connection}"
    elif ":" in connection:
        conn = f"TCP {connection}"
    else:
        conn = "???"

    secho(nvim.exec_lua(HEADER) + f"\nPID: {nvim.funcs.getpid()} Connection: {conn}")


@contextmanager
def nvim_attach(connection: str) -> Generator[Nvim, None, None]:
    """Attach to an nvim instance.

    This is the entrypoint for attaching to nvim servers using the standard Nvim
    API client for Python.

    In the case of socket or TCP address connections, this will connect to an
    existing nvim server instance listening at the connection path.

    In the case of embedded or embedded_clean, pynvim will spawn an instance of
    nvim with --embed and return an API client connected to it over stdin/stdout.
    This differs from lvim's "auto listen" functionality which also starts nvim,
    but listening on a TCP socket instead, in order to allow for multiple
    connections.

    Args:
        connection: str. Connection information to an nvim instance, or embedded.

    Yields:
        client: Nvim. Connected API client.
    """

    nvim = None
    try:
        if connection.startswith("embedded"):
            # Spawn nvim --embed subprocess and return client connected to it
            argv = ["/bin/env", "nvim", "--embed", "--headless"]

            # Spawn nvim no-config --embed subprocess and return client connected to it
            if connection == "embedded_clean":
                argv.append("--clean")

            logger.debug(f"Starting embedded nvim: {' '.join(argv)}")

            nvim = attach("child", argv=argv)
        elif "/" in connection:
            # Socket based connection
            logger.debug(f"Connecting to nvim server socket at {connection}")
            nvim = attach("socket", path=connection)
        elif ":" in connection:
            # nvim instance running with --listen
            logger.debug(f"Connecting to nvim server at {connection}")
            host, _, port = connection.rpartition(":")
            nvim = attach("tcp", address=host, port=int(port))
        else:
            raise ValueError(f"Unknown nvim connection string: {connection}")

        yield nvim
    except Exception as e:
        raise e
    finally:
        if nvim is not None:
            try:
                logger.debug("Closing nvim connection")
                nvim.close()
            except Exception:
                pass


@contextmanager
def parent_nvim(
    connection: Optional[str] = None,
    hide_header: bool = False,
    hide_notify: bool = False,
) -> Generator[Nvim, None, None]:
    """Connect to the "parent" nvim instance of an lvim session.

    This is the primary method for connecting to nvim servers. It will resolve
    any $NVIM environment variables, create embedded instances as needed, and
    connect to whatever it finds.

    Args:
        connection: Optional[str]. Connection string. If not provided, lvim will
            attempt to look up a connection via $NVIM in the environment.
        hide_header: bool. If True, don't display the connection header in the
            lvim REPL.
        hide_notify: bool. If True, don't display the client attachment
            notification in the parent nvim instance.

    Yields:
        nvim: Nvim. Nvim instance connected to parent nvim.

    Raises:
        ValueError: If no connection string is provided and no $NVIM var is set.
    """

    if connection is None:
        connection = nvim_connection()
        if not connection:
            raise ValueError("No connection provided or $NVIM variable set")

    pid = getpid()
    with nvim_attach(connection) as nvim:
        if not hide_notify:
            nvim.exec_lua(f"vim.notify('I [lvim] Client attached with PID: {pid}')")

        if not hide_header:
            show_header(nvim, connection)

        yield nvim

        if not hide_notify:
            nvim.exec_lua(f"vim.notify('I [lvim] Detached client with PID: {pid}')")
