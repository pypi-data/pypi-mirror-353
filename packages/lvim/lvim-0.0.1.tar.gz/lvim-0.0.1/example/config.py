#!/usr/bin/env python3
"""
Configuration example for lvim

Copy this file to $XDG_CONFIG_HOME/lvim/config.py
On Linux, this is: ~/.config/lvim/config.py
On macOS, this is: ~/Library/Application Support/lvim/config.py
"""

from lvim.repl import REPL
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import ViInsertMode
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts.prompt import CompleteStyle
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name


def configure(repl: REPL) -> None:
    """Configure the lvim prompt and add key bindings.

    See prompt_toolkit.shortcuts.prompt.PromptSession for info on available
    configuration fields. All commented configuration below shows the defaults
    for it.

    More info: https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#the-promptsession-object

    Args:
        repl: REPL. lvim REPL instance being configured, this is a subclass of
            PromptSession
    """

    # These are uncommented to set some sane defaults for lvim
    # Enable autocompletion while typing
    repl.complete_while_typing = False

    # CompleteStyle.MULTI_COLUMN or CompleteStyle.READLINE_LIKE
    repl.complete_style = CompleteStyle.MULTI_COLUMN

    # When True, going back in history will filter the history on the records
    # starting with the current input. (Like readline.)
    # Note: When enable, please disable the `complete_while_typing` option.
    #       otherwise, when there is a completion available, the arrows will
    #       browse through the available completions instead of the history.
    repl.enable_history_search = True

    # prompt_toolkit.styles.BaseStyle instance for the color scheme
    repl.style = style_from_pygments_cls(get_style_by_name("solarized-dark"))

    # When True, include the default styling for pygments lexers
    # If another pygments style was set in repl.style, this should probably be
    # set to False to avoid combining it with the default
    repl.include_default_pygments_style = False

    # EditingMode.VI or EditingMode.EMACS
    repl.app.editing_mode = EditingMode.VI

    # Additional key bindings
    bindings = KeyBindings()
    repl.key_bindings = bindings

    # Typing 'jk' in Vi Insert mode, should send escape. (Go back to navigation
    # mode)
    @bindings.add_binding("j", "k", filter=ViInsertMode())
    def _(event: KeyPressEvent) -> None:
        "Map 'jk' to Escape"
        event.cli.key_processor.feed(KeyPress(Keys("escape")))

    # These all show the default values, uncomment to change them
    # Plain text or formatted text to be shown before the prompt
    # See lvim.defaults.get_prompt for the default
    # repl.message = get_prompt
    # This can also be a callable that returns AnyFormattedText
    # above for the default
    # def func(
    #     prompt_width: int, line_number: int, wrap_count: int
    # ) -> AnyFormattedText:
    #     ...
    # repl.prompt_continuation = func

    # Text that needs to be displayed for a multiline prompt continuation, by
    # default, prompt_width spaces will be used
    # repl.prompt_continuation = None
    # This can either be AnyFormattedText or a callable
    # def func(
    #     prompt_width: int, line_number: int, wrap_count: int
    # ) -> AnyFormattedText:
    #     ...
    # repl.prompt_continuation = func

    # Text or formatted text to be displayed on the right side
    # repl.rprompt = None
    # This can also be a callable that returns AnyFormattedText
    # def func() -> AnyFormattedText:
    #     ...
    # repl.rprompt = func

    # When True, prefer a layout that is more adapted for multiline input.
    # Text after newlines is automatically indented, and search/arg input is
    # shown below the input, instead of replacing the prompt
    # repl.multiline = False

    # When True (the default), automatically wrap long lines instead of
    # scrolling horizontally
    # repl.wrap_lines = True

    # Show asterisks instead of the actual typed characters
    # repl.is_password = False

    # Enable input validation while typing
    # repl.validate_while_typing = True

    # Search case insensitive
    # repl.search_ignore_case = False

    # When True, pressing Meta+! will show a system prompt
    # This can also be a prompt_toolkit.filters.Filter
    # repl.enable_system_prompt = False

    # When True, enable Control-Z style suspension
    # This can also be a prompt_toolkit.filters.Filter
    # repl.enable_suspend = False

    # When True, pressing v in Vi mode or C-X C-E in emacs mode will open an
    # external editor
    # This can also be a prompt_toolkit.filters.Filter
    # repl.enable_open_in_editor = False

    # Space to be reserved for displaying the menu
    # (0 means that no space needs to reserved.)
    # repl.reserve_space_for_menu = 8

    # prompt_toolkit.auto_suggest.AutoSuggest instance for input suggestions
    # repl.auto_suggest = None

    # prompt_toolkit.style.StyleTransformation instance
    # repl.style_transformation = None

    # When True, apply prompt_toolkit.style.SwapLightAndDarkStyleTransformation
    # This is useful for switching between dark and light terminal backgrounds
    # This can also be a prompt_toolkit.filters.Filter
    # repl.swap_light_and_dark_colors = False

    # Set color depth (keep in mind that not all terminals support true color)
    # By default, this is derived from the output terminal, see
    # prompt_toolkit.Output.get_default_color_depth
    # repl.color_depth = None
    # repl.color_depth = ColorDepth.DEPTH_1_BIT  # Monochrome
    # repl.color_depth = ColorDepth.DEPTH_4_BIT  # ANSI colors only
    # repl.color_depth = ColorDepth.DEPTH_8_BIT  # The default, 256 colors
    # repl.color_depth = ColorDepth.DEPTH_24_BIT  # True color

    # prompt_toolkit.cursor_shapes.CursorShape for cursor display, by default,
    # no cursor shape sequences will be sent
    # repl.cursor = None
    # repl.cursor = CursorShape.BLOCK
    # repl.cursor = CursorShape.BEAM
    # repl.cursor = CursorShape.UNDERLINE
    # repl.cursor = CursorShape.BLINKING_BLOCK
    # repl.cursor = CursorShape.BLINKING_BEAM
    # repl.cursor = CursorShape.BLINKING_UNDERLINE
    #
    # This can also be set to a custom CursorShapeConfig which implements a
    # method get_cursor_shape(app) which can change the cursor based on state,
    # for example, prompt_toolkit.cursor_shapes.ModalCursorShapeConfig can be
    # used to change the cursor based on the current vi mode:
    # repl.cursor = ModalCursorShapeConfig()

    # prompt_toolkit.history.History instance to use for tracking and optionally
    # persisting history. By default this is
    # repl.history = None

    # prompt_toolkit.clipboard.base.Clipboard instance to use for managing the
    # clipboard. By default this is InMemoryClipboard which will not integrate
    # with system clipboards or persist between lvim sessions
    # repl.clipboard = None

    # Formatted text to display as a bottom toolbar
    # repl.bottom_toolbar = None
    # This can also be a callable that returns AnyFormattedText
    # def func() -> AnyFormattedText:
    #     ...
    # repl.message = func

    # When True, enable mouse support
    # This can also be a prompt_toolkit.filters.Filter
    # repl.mouse_support = False

    # List of additional prompt_toolkit.processors.Processor instances for
    # transforming user input, if any
    # repl.input_processors = None

    # Formatted text to be displayed when no input has been given yet
    # Unlike the `default` parameter, this won't be returned as part of the
    # output ever
    # repl.placeholder = None
    # This can also be a callable that returns AnyFormattedText
    # def func() -> AnyFormattedText:
    #     ...
    # repl.placeholder = func

    # The tempfile suffix (extension) to be used for the "open in editor" function
    # For lvim, this would be ".lua", so that the editor knows the
    # syntax highlighting to use
    # repl.tempfile_suffix = ".txt"
    # This can also be a callable that returns a string
    # def func() -> str:
    #     ...
    # repl.tempfile_suffix = func

    # For more advanced tempfile situations where you need control over the
    # subdirectories and filename. For a Git Commit Message, this would be
    # ".git/COMMIT_EDITMSG", so that the editor knows the syntax highlighting
    # to use
    # repl.tempfile = None
    # This can also be a callable that returns a string
    # def func() -> str:
    #     ...
    # repl.tempfile = func

    # When >0, refresh the UI every refresh_interval seconds
    # repl.refresh_interval = 0

    # The exception type that will be raised when there is a keyboard interrupt
    # (control-c keypress)
    # repl.interrupt_exception = KeyboardInterrupt

    # The exception type that will be raised when there is an end-of-file/exit
    # event (control-d keypress)
    # repl.eof_exception = EOFError

    # When True, clear the application output when it finishes
    # repl.app.erase_when_done = False

    # Generally these are not overridden in user config, but differ from defaults
    # When True, run the completer code in a background thread in order to avoid
    # blocking the user interface
    # For CompleteStyle.READLINE_LIKE, this setting has no effect. There
    # we always run the completions in the main thread
    # This can also be a prompt_toolkit.filters.Filter
    # repl.complete_in_thread = True

    # prompt_toolkit.lexers.Lexer to be used for syntax highlighting, by default
    # this is pygments.lexers.scripting.LuaLexer
    # repl.lexer = PygmentsLexer(LuaLexer)

    # prompt_toolkit.validation.Validator instance for input validation
    # repl.validator = None

    # prompt_toolkit.completion.Completer instance for input completion, by
    # default this is lvim.completer.NvimCompleter
    # repl.completer = NvimCompleter(repl.vim)
