#!/usr/bin/env python3

from getpass import getuser
from pathlib import Path

from click import style
from lvim.utils import format_path
from platformdirs import PlatformDirs
from prompt_toolkit.formatted_text import ANSI

PLATFORM_DIRS = PlatformDirs("lvim", "aemiller")


def default_config_home() -> Path:
    """Default --config / $LVIM_CONFIG_HOME path for this platform.

    Unix: ~/.config/lvim
    macOS: ~/Library/Application Support/lvim
    Windows: %USERPROFILE%\\AppData\\Local\\aemiller\\lvim
             %USERPROFILE%\\AppData\\Roaming\\aemiller\\lvim
    """

    return PLATFORM_DIRS.user_config_path


def default_history_file() -> Path:
    """Default --history file path for this platform.

    Unix: ~/.local/share/lvim/history
    macOS: ~/Library/Application Support/lvim/history
    Windows: %USERPROFILE%\\AppData\\Local\\aemiller\\lvim\\history
             %USERPROFILE%\\AppData\\Roaming\\aemiller\\lvim\\history
    """

    return PLATFORM_DIRS.user_data_path / "history"


def get_prompt() -> ANSI:
    """Get the prompt for a new line.

    Currently the prompt is formatted as:
    aemiller@nvim://|⇒

    Where:
    * `aemiller` - Current user running lvim
    * `//`       - Current nvim working directory, formatted relative to %pin

    Returns:
        prompt: ANSI. Prompt text in prompt_toolkit wrapper which indicates
            ANSI formatting
    """

    path, synced = format_path()

    return ANSI(
        style(getuser(), fg="magenta")
        + style("@", fg="cyan")
        + style("nvim", fg="bright_magenta")
        + style(":", fg="red")
        + style(path + ("!" if not synced else ""), fg="cyan")
        + style("|", fg="red")
        + style("⇒ ", fg="cyan")
    )
