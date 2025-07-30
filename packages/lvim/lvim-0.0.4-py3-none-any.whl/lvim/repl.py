#!/usr/bin/env python3
from __future__ import annotations

from logging import Logger, getLogger
from pathlib import Path
from shlex import split
from sys import stdin
from traceback import print_exc
from typing import Optional

from click import secho
from lvim.completer import NvimCompleter
from lvim.defaults import get_prompt
from lvim.magics import Exit, handle_magic
from lvim.utils import get_cwd, update_cd, update_cwd
from prompt_toolkit.history import (
    FileHistory,
    History,
    InMemoryHistory,
    ThreadedHistory,
)
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts.prompt import PromptSession
from pygments.lexers.scripting import LuaLexer
from pynvim import Nvim, NvimError

logger: Logger = getLogger(__name__)


# pyre-ignore[11]: Annotation `PromptSession` is not defined as a type
class REPL(PromptSession[str]):
    """The main Read-eval-print-loop (REPL) for lvim.

    This implements a prompt based interface to a connected nvim server using
    the prompt_toolkit library. It is a pure-Python alternative to other similar
    things such as GNU readline (via pyreadline) or linenoise. IPython's terminal
    REPLs also use it.

    The REPL itself is implemented as a combination of Lua, :ex commands, as
    well as lvim-specific %magics

    Prompt completion itself is implemented using the prompt_toolkit Completer
    interface. See the completer module for more info. Otherwise, it uses the
    built-in Lua lexer and solarized dark theme from the pygments library.

    The REPL is configured via the "configure" function in the config.py file
    located in the config home, by default ~/.config/lvim/config.py on *nix. An
    example configuration is located at example/config.py

    TODO: Multi-line input using do...end closures

    Args:
        nvim: Nvim. Connected API client, typically provided by an NvimSession.
        config_path: Path. Path to read lvim config.
        history_path: Path. Path to store lvim shell history.
        broker_channel: int. If an NvimBroker instance is started, this will be
            the channel ID that can be used to notify it with rpcnotify()
            Otherwise, it will default to 0, which notifies all connected clients.

    Public Attributes:
        vim: Nvim. Connected Nvim API client provided used by the REPL for
            executing user input and via magic functions.
        interactive: bool. Whether or not this is an interactive lvim session,
            that is, one that is running in a pty. This controls some behaviors
            around things like output coloring when being used in non-pty places
            like a pipe.
    """

    def __init__(
        self,
        nvim: Nvim,
        config_path: Path,
        history_path: Path,
        broker_channel: int = 0,
    ) -> None:
        self.vim = nvim
        self._cwd: Optional[Path] = None
        self.interactive: bool = stdin.isatty()
        self.config_path = config_path
        self.history_path = history_path

        # 0 = all channels
        self.broker_channel: int = broker_channel

        history: Optional[History] = None
        if history_path:
            history = ThreadedHistory(FileHistory(history_path))
        else:
            history = InMemoryHistory()

        super().__init__(
            # Initialize with the "defaults", which can be optionally overwritten
            # during configure() for anything that differs from PromptSession
            message=get_prompt,
            history=history,
            complete_in_thread=True,
            completer=NvimCompleter(self.vim),
            lexer=PygmentsLexer(LuaLexer),
        )

    def configure(self) -> None:
        """Configure the REPL.

        Taken from the equivalent ptpython function:
        https://github.com/prompt-toolkit/ptpython/blob/836431ff6775aac2c2e3aafa3295b259ebe99d0a/src/ptpython/repl.py#L453

        This will load the lvim config file at the path given and call the
        configure() function defined within it, passing a reference to the REPL
        itself in order to allow for changing overall config.
        """

        if not self.config_path.exists():
            logger.debug(f"No lvim config file at {self.config_path}")
            return

        # Run the config file in an empty namespace
        try:
            namespace = {}

            code = compile(self.config_path.read_text(), self.config_path, "exec")
            exec(code, namespace, namespace)

            if configure := namespace.get("configure", None):
                # Run configure() method from file with this REPL
                configure(self)
            else:
                logger.debug(
                    f"No configure function in config file at {self.config_path}"
                )
        except Exception:
            print_exc()
            input("\nPress ENTER to continue...")

    def start(self) -> None:
        """Start the Read-eval-print-loop.

        This will run indefinitely, prompting for user input and submitting it
        to the connected nvim instance, until it is stopped either via the %exit
        magic, or Ctrl-C/KeyboardInterrupt Ctrl-D/EOFError.

        The working directory is based on the cwd of nvim itself, and can be
        changed with the %cd magic.
        """

        self.configure()
        while True:
            update_cwd()
            update_cd()

            try:
                # Get line of input
                text = self.read_line()
            except Exit:
                # Exit exception from (ctrl)d, exit REPL
                break

            if text:
                try:
                    # Handle input
                    self.handle_line(text)
                except Exit:
                    # Exit exception from %exit magic, exit REPL
                    break

    @property
    def cwd(self) -> Path:
        """Get the current working directory of nvm.

        This is kept in sync with the cwd of the nvim instance via getcwd() and
        is the root for any operations which take a relative path as an argument.
        """

        return get_cwd()

    def read_line(self) -> Optional[str]:
        """Read a line of input from the lvim REPL.

        In the context of Lua, this will be a "chunk" of code to be submitted to
        nvim for execution. Each chunk is executed in it's own scope, so a local
        defined on one line will not be available in another. Variables can be
        persisted either using normal Lua globals or by enclosing multiple
        statements in a do...end closure (or a function).

        Returns:
            user_input: Optional[str]. Line of user input, or None if they
                pressed Ctrl-C to discard the line.

        Raises:
            Exit: This signals to the REPL that Ctrl-D has been pressed and an
                EOF has been sent for shutdown.
        """

        # Get line of input
        try:
            return self.prompt()
        except KeyboardInterrupt:
            # (ctrl)c -> Discard current line
            # TODO: This doesn't seem to work right now, and just exits
            return None
        except EOFError:
            # (ctrl)d -> Exit
            raise Exit()

    def handle_line(self, text: str) -> None:
        """Handle a line of user input from the prompt.

        By default, the prompt functions as a Lua interpreter, which uses the nvim
        exec_lua() RPC call to run it in the connected nvim instance. Functionally,
        it is similar to :lua print("foo") or :lua = vim.version()

        Input lines that start with % will be interpreted as a "magic" function,
        similar to the macro system of the same name in IPython. See the magics
        module and handle_magic() or enter % followed by a tab for completion.

        Outputs are printed to stdout, however any statements with side effects
        will be visible in the REPL, ie a global variable defined on one line
        will still be on another.

        Exceptions other than exit related ones are handled via REPL.handle_error()

        Args:
            text: str. User input text.

        Raises:
            Exit, KeyboardInterrupt, EOFError: If the user requested REPL shutdown
                via the %exit magic, Ctrl-C, or Ctrl-D while handling the line.
        """

        try:
            # TODO: Something like IPython's automagic that implicitly handles
            # magics without % as long as there is no variable defined with the
            # same name would be nice
            if text == "exit" or text == "clear":
                out = handle_magic(self, text)
            elif text.startswith("%"):
                # Run %magic command for internal REPL macros
                magic, _, args = text.partition(" ")
                out = handle_magic(self, magic, *split(args))
            elif text.startswith("!"):
                # Run shell via :! ex command
                out = self.nvim_exec_cmd(f":!{text[1:]}")
            elif text.startswith(":"):
                # Run vim :ex command via nvim RPC
                out = self.nvim_exec_cmd(text)
            else:
                # Execute lua input via nvim RPC
                out = self.nvim_exec_lua(text)

            return self.write(self.format_output(out), fg="green")
        except (Exit, KeyboardInterrupt, EOFError) as e:
            raise e
        except Exception as e:
            # Display formatted error to the user
            self.handle_error(e)

    def handle_error(self, err: Exception) -> None:
        """Handle an exception encountered while handling a line of user input.

        Right now this just prints the exception, adding color in an interactive
        session.
        """

        secho(err, fg="red")

    def write(self, out: str, fg: Optional[str] = None) -> None:
        """Write to stdout.

        Args:
            out: str. Output, usually from handling a line of input.
            fg: Optional[str]. An ANSI color to apply to the text in an
                interactive session.
        """

        secho(out, fg=fg)

    def format_output(self, text: Optional[str]) -> str:
        """Format the output from handling a line of input.

        In interactive mode, this will strip the quotes around string values,
        and converts None to an empty string.
        """

        # None is not nil, which is returned as "nil"
        if text is None:
            return ""

        text = str(text)

        # Strip initial quotes if interactive mode
        if (
            self.interactive
            and len(text) > 2
            and (text[0] == text[-1])
            and text.startswith(("'", '"'))
        ):
            return text[1:-1]
        else:
            return text

    def nvim_exec_cmd(self, text: str) -> str:
        """Run a vim :ex command on the nvim instance.

        Input lines that start with : will be interpreted as an ex command:

        aemiller@nvim://|⇒ :echo "foo"
        foo

        To see ex commands, enter : followed by a tab for completion.

        Args:
            cmd: str. :ex command text from user input.

        Returns:
            result: str. Output from the :ex command, if any.
        """

        return self.vim.command_output(text)

    def nvim_exec_lua(self, text: str) -> str:
        """Execute a chunk of Lua code on the nvim instance.

        The Lua interpreter will only execute statements, not single expressions,
        which doesn't really match the expectation for interactive use. To work
        around this, lvim will first try to wrap the user provided input in a
        return statement, ie vim.version() becomes return vim.version() which then
        makes it a valid statement:

        aemiller@nvim://|⇒ vim.api  -- return vim.inspect(vim.api)
        ... Contents of vim.api table from inspect ...

        aemiller@nvim://|⇒ print("foo")  -- return print("foo")
        nil

        This may seem a bit strange, but it is actually the same thing that the
        reference PUC Lua interpreter provided with the language does:

        https://github.com/lua/lua/blob/3fb7a77731e6140674a6b13b73979256bfb95ce3/lua.c#L630

        This is also what the ":lua =" shorthand does in nvim itself. Single
        expressions are also wrapped in vim.inspect() to provide a human-readable
        representation back to the REPL itself via the inspect library:

        https://github.com/kikito/inspect.lua

        Args:
            chunk: str. Chunk of Lua code from user input.

        Returns:
            result: str. Output from the chunk formatted as a string, if any.

        Raises:
            NvimError: If the provided chunk of code is invalid or encounters
                errors during execution. This will be handled by the REPL via
                handle_error()
        """

        try:
            return self.vim.exec_lua(f"return vim.inspect({text})")
        except NvimError as e:
            if not str(e).startswith("Error loading lua"):
                raise e

        # Try running as is, as a statement, which never returns a value itself
        # foo = 1
        try:
            return self.vim.exec_lua(text)
        except NvimError as e:
            raise e
