#!/usr/bin/env python3
from typing import Iterable

from lvim.magics import magic_names
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    WordCompleter,
)
from prompt_toolkit.document import Document
from pynvim import Nvim


class NvimCompleter(Completer):
    """Auto-completion interface for lvim.

    This provides tab completion for lua/ex/shell/magic inputs, largely relying
    on calling their equivalent completion methods on the nvim instance via RPC.

    Args:
        nvim: Nvim. Connected API client, typically provided by an NvimSession.
    """

    def __init__(self, nvim: Nvim) -> None:
        self.nvim = nvim
        self.magic_completer = WordCompleter(magic_names())

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """Get a completion(s) for the current line.

        This is the entrypoint called by prompt_toolkit when the user requests
        a completion (ie via tab) which routes to the correct completion function
        based on current input.

        Args:
            document: Document. Reference to the prompt_toolkit Document
                representation of the current input.
            complete_event: CompleteEvent. Additional metadata about how the
                completion was requested.

        Yields:
            completions: Iterable[Completion]. All generated completions for the
                current user input.
        """

        # :h getcompletion
        text = document.text
        if text == "exit":
            yield Completion(text="exit")
        elif text == "clear":
            yield Completion(text="clear")
        elif text.startswith("%"):
            # Complete magic using PT's built-in WordCompleter
            # This is a simple completion against all registered magic names.
            # aemiller@nvim://|⇒ %c<tab>
            # { "clear", "cd" }
            yield from self.magic_completer.get_completions(document, complete_event)
            # yield from self.magic_completions(document)
        elif text.startswith("!"):
            # Complete shell commands
            yield from self.shell_completions(document)
        elif text.startswith(":"):
            # Complete ex commands
            yield from self.cmd_completions(document)
        else:
            # Complete lua code
            yield from self.lua_completions(document)

    def shell_completions(self, document: Document) -> Iterable[Completion]:
        """Complete a shell command.

        A shell command is prefixed with ! and is handled by the :ex cmdline
        interface in nvim. This will use the getcompletion() function to generate
        completions in the shell environment of the nvim instance.

        These two forms are equivalent:

        aemiller@nvim://|⇒ ! ec<tab>
        vim.fn.getcompletion(":! ec", "cmdline")
        { "ecdh_curve25519", "ecdsa", "echo" }

        aemiller@nvim://|⇒ !ec<tab>
        vim.fn.getcompletion(":!ec", "cmdline")
        { "ecdh_curve25519", "ecdsa", "echo" }

        Any space after the command is just file completion at the nearest space

        aemiller@nvim://|⇒ ! echo <tab>
        vim.fn.getcompletion(":!echo ", "cmdline")
        { "BUCK", "pyproject.toml", ... }

        Args:
            document: Document. Reference to the prompt_toolkit Document
                representation of the current input.

        Yields:
            completions: Iterable[Completion]. Completions representing all commands
                in the path or any files in the local directory for args.
        """

        text = document.text
        options = self.nvim.funcs.getcompletion(f":{text}", "cmdline")

        # abbreviate _ <s
        _, space, after = text.rpartition(" ")

        if after:
            # ! ec
            # -len("ec") == -2
            start_position = -len(after)

            if after.startswith("!"):
                # !ec
                # -len("!ec") + 1 == -2
                start_position += 1
        else:
            # ! echo <- with trailing space
            # Start a file completion under current cursor position
            start_position = 0

        for option in options:
            yield Completion(text=option, start_position=start_position)

    def cmd_completions(self, document: Document) -> Iterable[Completion]:
        """Complete an :ex command.

        A vim ex command is prefixed with : and is handled by the command_output()
        function in nvim.

        This will use getcompletion() to complete vim commands available on the
        nvim instance, including user commands:

        aemiller@nvim://|⇒ :ab<tab>
        vim.funcs.getcompletion(":ab", "cmdline")
        { "abbreviate", "abclear", "aboveleft" }

        Additional completions on the same line will be for any args the command
        has defined:

        aemiller@nvim://|⇒ :abbreviate <s<tab>
        vim.funcs.getcompletion(":abbreviate <s", "cmdline")
        { "<script>", "<silent>", "<special>" }

        Args:
            document: Document. Reference to the prompt_toolkit Document
                representation of the current input.

        Yields:
            completions: Iterable[Completion]. Completions representing vim
                ex and user commands with the provided prefix, or arguments to
                them for additional completions.
        """

        text = document.text
        options = self.nvim.funcs.getcompletion(text, "cmdline")

        # abbreviate _ <s
        _, space, after = text.rpartition(" ")

        # :abbreviate <s
        # -len("<s")
        # -2, completion is placed after the most recent space
        start_position = -len(after)
        if not space:
            # Completing command itself, don't overwrite the :
            # :ab
            # -len(":ab") + 1 = -2
            start_position += 1

        for option in options:
            yield Completion(text=option, start_position=start_position)

    def lua_completions(self, document: Document) -> Iterable[Completion]:
        """Complete a line of lua code.

        If a completion is requested that does not match one of the above handlers
        based on it's prefix, it will be completed as a line of Lua code in the
        interpreter of the nvim instance.

        This is currently just a direct shim to getcompletion() for the lua
        ex command, which will complete based on global variables, modules, and
        functions defined in the current environment, as well as any properties
        of them:

        aemiller@nvim://|⇒ vim.c<tab>
        vim.funcs.getcompletion("vim.c", "cmdline")
        { "call", "cmd" }

        Args:
            document: Document. Reference to the prompt_toolkit Document
                representation of the current input.

        Yields:
            completions: Iterable[Completion]. Completions representing lua
                values in the global namespace with the provided prefix.
        """

        text = document.text
        options = self.nvim.funcs.getcompletion(f"lua {text}", "cmdline")

        # -1, Completion is placed 1 char behind the cursor, after the .
        start_position = document.find_boundaries_of_current_word()[0]
        for option in options:
            yield Completion(text=option, start_position=start_position)
