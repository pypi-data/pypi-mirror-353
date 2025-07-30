#!/usr/bin/env python3
from logging import DEBUG, INFO, Logger, basicConfig, getLogger
from pathlib import Path
from typing import Optional, Tuple

import click
from lvim.context import Context
from lvim.defaults import default_config_home, default_history_file
from lvim.nvim import nvim_connection

logger: Logger = getLogger(__name__)


def init_logger(debug: bool = False) -> None:
    basicConfig(level=DEBUG if debug else INFO)


@click.command(name="lvim")
@click.option("--debug", is_flag=True, help="enable debug output")
@click.option("--no-header", is_flag=True, help="disable header")
@click.option(
    "--embed",
    is_flag=True,
    help="connect to new nvim --embed instance via stdin/stdout",
)
@click.option(
    "--clean",
    is_flag=True,
    help="(embed) run nvim with --clean to skip all state and user config",
)
@click.option(
    "--server",
    type=str,
    help="override and connect to this nvim server socket/address",
)
@click.option(
    "--listen",
    type=str,
    help="instead of auto-detection, start a headless nvim server at this socket/address and connect to it",
)
@click.option(
    "--no-broker",
    is_flag=True,
    help="don't start the nvim broker thread",
)
@click.option("--py", is_flag=True, help="start a Python session instead")
@click.option("--ipy", is_flag=True, help="start an IPython session instead")
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    help=f"path to config home (default {default_config_home()})",
    envvar="LVIM_CONFIG_HOME",
)
@click.option(
    "--history",
    type=click.Path(path_type=Path),
    help=f"path to history file (default {default_history_file()}",
)
@click.option(
    "--no-cd",
    is_flag=True,
    help="don't change lvim to the nvim current working directory on start",
)
@click.option(
    "--no-pin",
    is_flag=True,
    help="don't pin the nvim current working directory on start",
)
@click.argument("file", nargs=-1, type=str)
@click.pass_context
def lvim(
    click_ctx: click.Context,
    debug: bool,
    no_header: bool,
    embed: bool,
    clean: bool,
    server: Optional[str],
    listen: Optional[str],
    no_broker: bool,
    py: bool,
    ipy: bool,
    config: Optional[Path],
    history: Optional[Path],
    no_cd: bool,
    no_pin: bool,
    file: Tuple[str, ...],
) -> None:
    """luavim, an interactive REPL for Neovim's Lua(JIT) environment

    lvim is a remote control for nvim, heavily inspired by neovim-remote (nvr)
    by mhinz: https://github.com/mhinz/neovim-remote

    See README.md for more details on usage.
    """

    init_logger(debug=debug)

    if not server and not embed and not listen:
        server = nvim_connection()
        logger.debug(f"Using existing $NVIM connection at: {server}")

    config_home = config if config else default_config_home()
    config_path = config_home / "config.py"
    pyconfig_path = config_home / "pyconfig.py"

    logger.debug(f"Using lvim ptpython config at {config_path}")
    if not config_home.exists():
        logger.debug(f"Creating config home {config_home}")
        config_home.mkdir(parents=True)

    history_path = history if history else default_history_file()
    history_home = history_path.parent

    logger.debug(f"Using lvim ptpython history at {history_path}")
    if not history_home.exists():
        logger.debug(f"Creating history home {history_home}")
        history_home.mkdir(parents=True)

    # Create the lvim Context and set it on the current click.Context.
    # This is more or less what the ensure=True flag on make_pass_decorator
    # does under the hood, but this allows for constructing the Context with
    # our own arguments.
    ctx = Context(
        debug=debug,
        hide_header=no_header,
        embed=embed,
        clean=clean,
        connection=server,
        disable_broker=no_broker,
        listen=listen,
        config_path=config_path,
        pyconfig_path=pyconfig_path,
        history_path=history_path,
        no_cd=no_cd,
        no_pin=no_pin,
    )

    click_ctx.obj = ctx

    if not file:
        # No input files, start REPL
        if py or ipy:
            ctx.nvim_py_repl(ipy)
        else:
            ctx.nvim_lua_repl()
    else:
        # TODO: Implement open in editor for file args
        for cur_file in file:
            print(Path(cur_file))
