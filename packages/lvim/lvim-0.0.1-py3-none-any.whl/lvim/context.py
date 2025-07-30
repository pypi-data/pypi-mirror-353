#!/usr/bin/env python3
from __future__ import annotations

from contextlib import contextmanager, nullcontext
from logging import Logger, getLogger
from os import chdir
from pathlib import Path
from typing import Any, Callable, Generator, Optional

import click
from lvim.broker import NvimBroker
from lvim.nvim import nvim_start
from lvim.pyrepl import PyREPL
from lvim.repl import REPL
from lvim.session import NvimSession

logger: Logger = getLogger(__name__)


class Context:
    """Main lvim CLI context.

    This is called by the lvim CLI in order to initialize either the main REPL
    or IPython, and contains all related state.

    Args:
        config_path: Path. Path to read lvim config.
        config_path: Path. Path to read lvim python (--py/--ipy) config.
        history_path: Path. Path to store lvim shell history.
        debug: bool. Enable additional debug behavior and output.
        hide_header: bool. If True, don't display the header when starting the
            REPL.
        connection: Optional[str]. TCP host:port or socket of an nvim instance
            to connect to. If unset, this information will be discovered from
            the $NVIM variable in the tmux environment.
        listen: Optional[str]. TCP host:port or socket to use for starting a new
            nvim server instance to connect to. If unset, a socket path will be
            automatically derived from the local /tmp directory.
        embed: bool. If True, an embedded nvim instance will be started via
            pynvim which communicates with lvim via stdin/stdout. This is not
            the same as the listen server, as it only allows for one client.
        clean: bool. If True, run nvim with --clean, which will skip all user
            config and state.
        disable_broker: bool. If True, the NvimBroker will not be started for
            this lvim instance, which means it will not receive notifications.
        no_cd: bool. If True, don't change lvim to the current nvim working dir
            on start.
        no_pin: bool. If True, don't %pin the nvim current working dir on start

    Public Attributes:
        cwd: Path. Current working directory of the connected nvim instance.
        cd: Path. Current directory of the lvim process itself.
        pd: Path. Current directory pinned by %pin.
    """

    def __init__(
        self,
        config_path: Path,
        pyconfig_path: Path,
        history_path: Path,
        debug: bool = False,
        hide_header: bool = False,
        connection: Optional[str] = None,
        listen: Optional[str] = None,
        embed: bool = False,
        clean: bool = False,
        disable_broker: bool = False,
        no_cd: bool = False,
        no_pin: bool = False,
    ) -> None:
        self.debug = debug
        self.hide_header = hide_header
        self.connection = connection
        self.embed = embed
        self.clean = clean
        self.listen = listen
        self.no_cd = no_cd
        self.no_pin = no_pin
        self.config_path = config_path
        self.pyconfig_path = pyconfig_path
        self.history_path = history_path

        # If none of --embed/--listen/--server were provided, then auto-start a
        # listen server and connect to it
        self._auto_listen: bool = (
            not self.connection and not self.embed and not self.listen
        )
        self._listen_path: Optional[str] = None

        if not self.embed:
            self.disable_broker: bool = disable_broker
        else:
            # --embed doesn't offer any way for the second session to connect
            self.disable_broker = True

        self._nvim: Optional[NvimSession] = None
        self._broker: Optional[NvimBroker] = None

        # vim current workdir
        self.cwd: Path = Path("./")
        # lvim current dir
        self.cd: Path = Path("./")
        # lvim pinned directory
        self.pd: Path = Path("./")

    @property
    def connection_override(self) -> str:
        """Get the actual connection string based on user configuration.

        * If --server is provided, it is always used. This includes any value
          discovered in $NVIM by the CLI on startup
        * If --embed is provided, an embedded instance will be started and the
          REPL will connect to it without a broker session, since stdin/stdout
          only allow for one client
        * Otherwise, an nvim instance will be started in a background thread
          listening on a unix socket in the /tmp directory. The REPL and broker
          will connect to this instance, which will also be cleaned up on
          shutdown

        Returns:
            connection: str. Connection string to use for connecting to nvim.

        Raises:
            ValueError: If no connection value is set, and no listen server is
                running.
        """

        if self.connection:
            return self.connection
        elif self.embed:
            return "embedded" if not self.clean else "embedded_clean"
        elif self.listen or self._auto_listen:
            # Return the path to the auto-started listen server socket
            return self.listen_path
        else:
            raise ValueError("No connection set")

    @property
    def listen_path(self) -> str:
        """Get the path to the unix socket for the listen server, if started."""

        if not self._listen_path:
            raise ValueError("Listen server not started")

        return self._listen_path

    @listen_path.setter
    def listen_path(self, connection: str) -> None:
        """Set the path to the listen server after auto starting it."""

        self._listen_path = connection

    @contextmanager
    def server(self) -> Generator[None, None, None]:
        """Start the nvim listen server in a background thread."""

        logger.debug("Starting nvim --listen server")
        with nvim_start(
            self.listen if self.listen else "auto", self.clean
        ) as listen_path:
            self.listen_path = listen_path
            yield

    @contextmanager
    def attach(self) -> Generator[None, None, None]:
        """Attach to nvim.

        Using the provided configuration from the CLI, this will connect to
        nvim in order to create an NvimSession and NvimBroker to be used for
        the REPL.

        Each lifecycle stage has its own context, which will clean up after
        itself on shutdown.
        """

        maybe_listen_ctx = (
            self.server() if self.listen or self._auto_listen else nullcontext()
        )

        with maybe_listen_ctx:
            logger.debug("Creating nvim session")
            self.nvim = NvimSession(
                hide_header=self.hide_header,
                connection=self.connection_override,
                debug=self.debug,
            )

            logger.debug("Attaching to nvim session")
            with self.nvim.attach():
                self.update_cwd()

                # Move to the nvim working cwd on boot and pin it
                if not self.no_cd:
                    self.set_cd(self.cwd)
                if not self.no_pin:
                    self.set_pd(self.cwd)

                if not self.disable_broker:
                    logger.debug("Creating broker session")
                    self.broker = NvimBroker(parent=self.nvim, debug=self.debug)
                    broker_ctx = self.broker.attach()
                else:
                    logger.debug("Broker disabled!")
                    broker_ctx = nullcontext()

                logger.debug("Attaching to broker session context (if enabled)")
                with broker_ctx:
                    yield

    def nvim_py_repl(self, ipy: bool = False) -> None:
        """Start an embedded (I)Python session with the connected nvim client(s).

        This is an alternative to the normal lvim REPL which just uses ptython's
        embed functionality.

        The connected Nvim client will be available at `vim`, and the session
        and broker will be available at `_session` and `_broker`.

        ptpython code is split into PyREPL, which is available at `_repl`, with
        the underlying Prompt Toolkit input class at `_repl.pt`

        Args:
            ipy: bool. If True, IPython will be used as the interpreter backend
                for ptpython.
        """

        with self.attach():
            if not self.hide_header:
                click.secho(
                    "\nInfo:  %lsmagic                   -- or vim.command(':h lua-guide')"
                    f"\nUsage: print(vim.funcs.getcwd())  -- {self.cwd}\n"
                )

            repl = PyREPL(self.pyconfig_path, self.history_path, ipy)

            repl.start(
                # Make the connected Nvim client available at vim
                vim=self.nvim.vim,
                _session=self,
                _broker=self.broker,
                _repl=repl,
            )

    def nvim_lua_repl(self) -> None:
        """Start the lvim session.

        This is the entrypoint for lvim called by the CLI. It will attach to
        an nvim instance, creating it if necessary, and then start the main
        Read-eval-print-loop, which will run until shutdown is requested.
        """

        with self.attach():
            if not self.hide_header:
                click.secho(
                    "\nInfo:  %help                   -- or :h lua-guide"
                    f"\nUsage: print(vim.fn.getcwd())  -- {self.cwd}\n"
                )

            REPL(
                self.nvim.vim,
                config_path=self.config_path,
                history_path=self.history_path,
                broker_channel=self.broker.channel_id if self._broker else -1,
            ).start()

    def update_cwd(self) -> None:
        """Update the stored path for the cwd of the connected nvim instance."""

        self.cwd = Path(self.nvim.vim.funcs.getcwd())

    def set_cwd(self, path: Path) -> None:
        """Set the current working directory (cwd) of the nvim instance."""

        logger.debug(f"Setting vim cwd to {path}")
        self.nvim.vim.command(f":cd {path}")
        self.update_cwd()

    def update_cd(self) -> None:
        """Update the current directory of lvim."""

        self.cd = Path.cwd()

    def set_cd(self, path: Path) -> None:
        """Set the current directory of the lvim process."""

        logger.debug(f"Setting lvim cd to {path}")
        chdir(str(path))
        self.update_cd()

    def set_pd(self, path: Path) -> None:
        """Update the pinned directory.

        Args:
            path: Path. New path to pin.
        """

        logger.debug(f"Setting lvim pinned dir to {path}")
        self.pd = path

    @property
    def nvim(self) -> NvimSession:
        """NvimSession connected to the nvim instance used by this REPL."""

        if not self._nvim:
            raise ValueError("Nvim session is not connected")

        return self._nvim

    @nvim.setter
    def nvim(self, session: NvimSession) -> None:
        self._nvim = session

    @property
    def broker(self) -> NvimBroker:
        """NvimBroker handling notifications for this REPL, if enabled."""

        if not self._broker:
            raise ValueError("Broker session is not connected")

        return self._broker

    @broker.setter
    def broker(self, session: NvimBroker) -> None:
        self._broker = session


# Function decorator to pass global CLI context into a function.
# make_pass_decorator returns a generic function with this signature:
# Callable[[Concatenate[Context, P], Callable[P, R]]
# Indicating that the current Context is concatenated to the function's params
# pyre-ignore[5]: Globally accessible variable `pass_context` must be specified
# as type that does not contain `Any`.
pass_context: Callable[..., Any] = click.make_pass_decorator(Context, ensure=True)
