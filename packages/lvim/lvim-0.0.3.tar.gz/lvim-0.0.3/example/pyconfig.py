#!/usr/bin/env python3
"""
Configuration example for lvim's ptpython (--py) and ptipython (--ipy) REPLs

Copy this file to $XDG_CONFIG_HOME/lvim/pyconfig.py
On Linux, this is: ~/.config/lvim/pyconfig.py
On macOS, this is: ~/Library/Application Support/lvim/pyconfig.py
"""

from prompt_toolkit.filters import ViInsertMode
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyPressEvent
from prompt_toolkit.keys import Keys
from ptpython.python_input import PythonInput


def configure(repl: PythonInput) -> None:
    """
    Configure ptpython for the lvim --py and --ipy modes and add key bindings.

    Based on https://github.com/prompt-toolkit/ptpython/blob/main/examples/ptpython_config/config.py

    Args:
        repl: PythonInput. ptpython REPL instance being configured, this is either
            ptpython.repl.PythonRepl or ptpython.ipython.IPythonRepl depending
            on the mode that lvim was started with
    """

    # These are uncommented to set some sane defaults for lvim
    # Syntax.
    repl.enable_syntax_highlighting = True

    # Get into Vi navigation mode at startup
    repl.vi_start_in_navigation_mode = True

    # Enable vi mode instead of emacs
    repl.vi_mode = True

    # Enable the modal cursor (when using Vi mode). Other options are 'Block', 'Underline',  'Beam',  'Blink under', 'Blink block', and 'Blink beam'
    repl.cursor_shape_config = "Modal (vi)"

    # Paste mode. (When True, don't insert whitespace after new line.)
    # repl.paste_mode = False

    # Complete while typing. (Don't require tab before the
    # completion menu is shown.)
    repl.complete_while_typing = False

    # History Search.
    # When True, going back in history will filter the history on the records
    # starting with the current input. (Like readline.)
    # Note: When enable, please disable the `complete_while_typing` option.
    #       otherwise, when there is a completion available, the arrows will
    #       browse through the available completions instead of the history.
    repl.enable_history_search = True

    # Enable auto suggestions. (Pressing right arrow will complete the input,
    # based on the history.)
    repl.enable_auto_suggest = True

    # Ask for confirmation on exit.
    repl.confirm_exit = False

    # Use this colorscheme for the code.
    # Ptpython uses Pygments for code styling, so you can choose from Pygments'
    # color schemes. See:
    # https://pygments.org/docs/styles/
    # https://pygments.org/demo/
    # repl.use_code_colorscheme("default")
    # A colorscheme that looks good on dark backgrounds is 'native':
    # repl.use_code_colorscheme("native")
    repl.use_code_colorscheme("solarized-dark")

    # Additional key bindings
    # Typing 'jk' in Vi Insert mode, should send escape. (Go back to navigation
    # mode.)
    @repl.add_key_binding("j", "k", filter=ViInsertMode())
    def _(event: KeyPressEvent) -> None:
        "Map 'jk' to Escape."
        event.cli.key_processor.feed(KeyPress(Keys("escape")))

    # These all show the default values, uncomment to change them
    # Set custom prompt
    # Built-in options are classic (">>>") and ipython ("In [1]")
    # repl.all_prompt_styles["lvim"] = LvimPrompt(repl)
    # repl.prompt_style = "lvim"

    # Show function signature (bool).
    # repl.show_signature = False

    # Show docstring (bool).
    # repl.show_docstring = False

    # Show the "[Meta+Enter] Execute" message when pressing [Enter] only
    # inserts a newline instead of executing the code.
    # repl.show_meta_enter_message = True

    # Show completions. (NONE, POP_UP, MULTI_COLUMN or TOOLBAR)
    # repl.completion_visualisation = CompletionVisualisation.MULTI_COLUMN

    # When CompletionVisualisation.POP_UP has been chosen, use this
    # scroll_offset in the completion menu.
    # repl.completion_menu_scroll_offset = 1

    # Show line numbers (when the input contains multiple lines.)
    # repl.show_line_numbers = False

    # Show status bar.
    # repl.show_status_bar = True

    # When the sidebar is visible, also show the help text.
    # repl.show_sidebar_help = True

    # Swap light/dark colors on or off
    # repl.swap_light_and_dark = False

    # Highlight matching parentheses.
    # repl.highlight_matching_parenthesis = False

    # Line wrapping. (Instead of horizontal scrolling.)
    # repl.wrap_lines = True

    # Mouse support.
    # repl.enable_mouse_support = False

    # Fuzzy and dictionary completion.
    # repl.enable_fuzzy_completion = Fale
    # repl.enable_dictionary_completion = False

    # Don't insert a blank line after the output.
    # repl.insert_blank_line_after_output = True

    # Enable open-in-editor. Pressing C-x C-e in emacs mode or 'v' in
    # Vi navigation mode will open the input in the current editor.
    # repl.enable_open_in_editor = True

    # Enable system prompt. Pressing meta-! will display the system prompt.
    # Also enables Control-Z suspend.
    # repl.enable_system_bindings = False

    # Enable input validation. (Don't try to execute when the input contains
    # syntax errors.)
    # repl.enable_input_validation = True

    # Set color depth (keep in mind that not all terminals support true color).
    # repl.color_depth = None
    # repl.color_depth = ColorDepth.DEPTH_1_BIT  # Monochrome.
    # repl.color_depth = ColorDepth.DEPTH_4_BIT  # ANSI colors only.
    # repl.color_depth = ColorDepth.DEPTH_8_BIT  # The default, 256 colors.
    # repl.color_depth = ColorDepth.DEPTH_24_BIT  # True color.

    # Min/max brightness
    # repl.min_brightness = 0.0  # Increase for dark terminal backgrounds.
    # repl.max_brightness = 1.0  # Decrease for light terminal backgrounds.
    # Preserve last used Vi input mode between main loop iterations
    # repl.vi_keep_last_used_mode = False

    # Add a custom title to the status bar. This is useful when ptpython is
    # embedded in other applications.
    # repl.title = "lvim"
