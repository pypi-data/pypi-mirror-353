#!/usr/bin/env python3
"""lvim magic macros.

A magic is an interpreter local macro to control certain functions of the lvim
REPL. The format is the same as their IPython equivalents:

Clear the screen:
%clear (or just clear)

Change the working directory of nvim:
aemiller@nvim:~/|⇒ %ls
<contents of ~/>
aemiller@nvim:~/|⇒ %cd code
aemiller@nvim:~/code|⇒ %ls
<contents of ~/code>

To see all magics, enter % followed by a tab for completion, or run %magics to
list all currently registered macros.

A magic function gets a reference to the REPL that received it, as well as any
arguments provided afterwards as strings. It can optionally return output, which
will be displayed to the user.
"""

from __future__ import annotations

from logging import Logger, getLogger
from pathlib import Path
from textwrap import dedent
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    TypeAlias,
)

from click import secho
from lvim.utils import get_cd, get_cwd, get_pd, set_cd, set_cwd, set_pd
from prompt_toolkit.shortcuts import clear as pt_clear

if TYPE_CHECKING:
    from lvim.repl import REPL

    MagicFn: TypeAlias = Callable[[REPL, str], Optional[str]]

logger: Logger = getLogger(__name__)


class Exit(Exception):
    """Exception to signal REPL shutdown."""

    pass


def run_cmd(repl: REPL, name: str, *args: str, nargs: int = 0) -> str:
    """Run an :ex command in a magic.

    This is just a general interface to the REPL object's command execution
    function for magics which execute commands.

    Args:
        repl: REPL. Interpreter which is executing this magic.
        name: str.  :ex command name.
        *args: str. Any arguments provided to the magic.
        nargs: int. How many arguments this :ex command takes, for error checking.

    Returns:
        result: str. Output from the :ex command, if any.
    """

    if nargs and len(args) < nargs:
        raise ValueError(f"%{name} takes {nargs} argument(s), {len(args)} provided")

    return repl.nvim_exec_cmd(f":{name} {' '.join(args)}")


def cmd_alias(name: str, *cmd_args: str, nargs: int = 0) -> MagicFn:
    """Generate a %magic alias to an :ex command.

    For example, with %ls bound to cmd_alias(":!ls")
    aemiller@nvim://|⇒ %ls

    Will run :!ls and list files in the nvim cwd.

    Args:
        name: str. ex command name.
        *cmd_args: str. Any predefined arguments provided to the command.
        nargs: int. How many arguments this :ex command takes, for error checking.

    Returns:
        alias_fn: MagicFn. Function for command alias.
    """

    def magic_fn(repl: REPL, *args: str) -> Optional[str]:
        combined = cmd_args + args
        return run_cmd(repl, name, *combined, nargs=nargs)

    return magic_fn


def magic_alias(name: str, *magic_args: str) -> MagicFn:
    """Generate a %magic alias to an another magic function.

    For example, with %ping bound to magic_alias("%rpc", "lvim_ping")
    aemiller@nvim://|⇒ %ping

    Will run %rpc lvim_ping

    Args:
        name: str. Magic name.
        *magic_args: str. Any predefined arguments provided to the magic.

    Returns:
        alias_fn: MagicFn. Function for magic alias.
    """

    def magic_fn(repl: REPL, *args: str) -> Optional[str]:
        combined = magic_args + args
        return handle_magic(repl, name, *combined)

    return magic_fn


def handle_magic(repl: REPL, magic: str, *args: str) -> Optional[str]:
    """Handle a %magic function from user input in a REPL.

    This is called by REPL.handle_line and dispatches the provided user input
    to the magic function registered with the name provided.

    Args:
        repl: REPL. Interpreter which is executing this magic.
        magic: str. Magic function name.
        *args: str. Any arguments provided to the magic.

    Returns:
        result: Optional[str]. Output from the magic, if any.
    """

    if func := _MAGICS[magic]:
        return func(repl, *args)
    else:
        raise ValueError(f"No magic defined with name %{magic}")


def clear(repl: REPL, *args: Any) -> None:
    """%clear - Clear the terminal screen.

    This just calls the prompt_toolkit shortcut clear(), which wipes the screen
    and resets the cursor back to the home position in the given prompt session.

    Can also be invoked with just clear
    """

    pt_clear()


def pin(repl: REPL, *args: str) -> str:
    """%pin <dir> - Change the lvim pinned directory.

    The pinned directory is used for prompt formatting and is shown as "//"
    by default. All paths relative to the pinned dir will be formatted with
    the same prefix:

    Pin the directory at ./lvim
    ~/|⇒ %pin lvim
       cwd == /home/aemiller
       cd  == /home/aemiller
       pd  == /home/aemiller/lvim
    ~/|⇒ %cd lvim
    //|⇒

    No args, print the current pinned dir
    //|⇒ %pin
    "/home/aemiller/lvim"
    """

    nargs = len(args)
    if nargs > 1:
        raise ValueError(f"%pin takes 1 argument, {len(args)} provided")
    elif nargs == 1:
        return str(set_pd(Path(args[0])))
    else:
        return str(get_pd())


def pin_bang(repl: REPL, *args: str) -> str:
    """%pin! <dir> - Change or sync the current pinned dir.

    This functions the same as %pin with an argument, but without an argument,
    it will sync the lvim cd to be the pinned directory.

    Pin the directory at ./lvim
    ~/|⇒ %pin! lvim
       cwd == /home/aemiller
       cd  == /home/aemiller
       pd  == /home/aemiller/lvim
    ~/|⇒ %cd lvim
    //|⇒

    No args, pin the lvim working dir
    //src|⇒ %pin!
       cwd == /home/aemiller/lvim/src
       cd  == /home/aemiller/lvim/src
       pd  == /home/aemiller/lvim/src
    //|⇒
    """

    nargs = len(args)
    if nargs > 1:
        raise ValueError(f"%pin takes 1 argument, {len(args)} provided")
    elif nargs == 1:
        return str(set_pd(Path(args[0])))
    else:
        return str(set_pd(get_cd()))


def cwd(repl: REPL, *args: str) -> str:
    """%cwd <dir> - Change the nvim current working dir (cwd).

    This changes the current working directory of the connected nvim instance
    itself. See :h current-directory

    Change nvim current working dir, leaving it out of sync with lvim cd
    //|⇒ %cwd src
       cwd == /home/aemiller/lvim/src
       cd  == /home/aemiller/lvim
    //!|⇒

    When the nvim cwd and lvim cd are out of sync, an (!) will be displayed after
    the path. Use :cd! with no args to bring them in sync, or just change the
    lvim cd as well:
    //!|⇒ %cd src
    //src|⇒

    No args, print the nvim current working dir
    //src|⇒ %cwd
    "/home/aemiller/lvim/src"
    """

    nargs = len(args)
    if nargs > 1:
        raise ValueError(f"%cd takes 1 argument, {len(args)} provided")
    elif nargs == 1:
        return str(set_cwd(Path(args[0])))
    else:
        return str(get_cwd())


def cd(repl: REPL, *args: str) -> str:
    """%cd <dir> - Change the lvim current directory.

    This changes the working directory of the lvim process, similar to running
    cd in a shell. To change the working directory of nvim itself, see %cwd

    Change lvim working dir, leaving it out of sync with the nvim cwd
    //|⇒ %cd src
       cwd == /home/aemiller/lvim
       cd  == /home/aemiller/lvim/src
    //src!|⇒ %cd!

    No args, print the current lvim working dir
    //src!|⇒ %cd
    "/home/aemiller/lvim/src"
    """

    nargs = len(args)
    if nargs > 1:
        raise ValueError(f"%cd takes 1 argument, {len(args)} provided")
    elif nargs == 1:
        return str(set_cd(Path(args[0])))
    else:
        return str(Path.cwd())


def cd_bang(repl: REPL, *args: str) -> str:
    """%cd! <dir> - Change and/or sync the lvim current dir.

    Change lvim working dir and nvim cwd to the same path
    //|⇒ %cd! src
       cwd == /home/aemiller/lvim/src
       cd  == /home/aemiller/lvim/src
    //src|⇒ %cd! src

    No args, sync nvim cwd to with lvim working dir
    //src!|⇒ %cd!
       cwd == /home/aemiller/lvim/src
       cd  == /home/aemiller/lvim/src
    //src|⇒
    """

    nargs = len(args)
    if nargs > 1:
        raise ValueError(f"%cd takes 1 argument, {len(args)} provided")
    elif nargs == 1:
        new_path = Path(args[0])
        set_cwd(new_path)
        return str(set_cd(new_path))
    else:
        return str(set_cwd(get_cd()))


def exit_repl(repl: REPL, *args: str) -> None:
    """%exit - Shut down the REPL.

    This magic (or just exit) can be used to quit lvim via the prompt.
    """

    raise Exit()


def rpc_notify(repl: REPL, *args: str) -> None:
    """%rpc <args> - Manually send a notification to the lvim broker."""

    if repl.broker_channel == -1:
        raise ValueError("Broker not running, cannot use %rpc")
    elif not args:
        raise ValueError("%rpc missing required argument 'name'")

    repl.vim.funcs.rpcnotify(repl.broker_channel, args[0], *args[1:])


def list_magics(repl: REPL, *args: str) -> None:
    """%magics - List all currently registered magics."""

    for magic in magic_names():
        secho(magic, fg="green")


def help(repl: REPL, *args: str) -> None:
    """%help <magic> - Show information for a magic."""

    nargs = len(args)
    if nargs > 1:
        raise ValueError(f"%help takes 1 argument, {nargs} provided")
    elif nargs == 1:
        name = args[0]

        if not name.startswith("%"):
            name = f"%{name}"
    else:
        name = "%help"

    if docstring := _MAGICS[name].__doc__:
        secho(dedent(f"    {docstring}"))


def magic_names() -> List[str]:
    """Get a list of all currently registered magic names."""

    return list(_MAGICS.keys())


# Magics are registered by name to their user defined or generated handler function.
_MAGICS: Dict[str, MagicFn] = {
    # TODO: Something like %rehashx for these
    "%split": cmd_alias(":split"),
    "%vsplit": cmd_alias(":vsplit"),
    "%lsb": cmd_alias(":ls"),
    "%ls": cmd_alias(":!ls"),
    "%magics": list_magics,
    "%cwd": cwd,
    "%cd": cd,
    "%cd!": cd_bang,
    "%pin": pin,
    "%pin!": pin_bang,
    "%clear": clear,
    "clear": clear,
    "%exit": exit_repl,
    "exit": exit_repl,
    "%rpc": rpc_notify,
    "%ping": magic_alias("%rpc", "lvim_ping"),
    "%help": help,
}
