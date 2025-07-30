#!/usr/bin/env python3
from logging import Logger, getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import click

if TYPE_CHECKING:
    from ptpython.python_input import PythonInput

logger: Logger = getLogger(__name__)


class PyREPL:
    """An nvim-connected (I)Python interpreter provided by prompt_toolkit.

    This is a wrapper around ptpython/ptipython with some custom configuration
    and macros specific to lvim and the pynvim SDK:
    https://github.com/prompt-toolkit/ptpython

    The REPL is configured via the "configure" function in the pyconfig.py file
    located in the config home, by default ~/.config/lvim/pyconfig.py on *nix. An
    example configuration is located at example/pyconfig.py

    Args:
        pyconfig_path: Path. Path to read lvim pyconfig.
        history_path: Path. Path to store lvim shell history.
        ipy: bool. If True, launch ptipython instead of ptpython (IPython required).
    """

    def __init__(
        self,
        pyconfig_path: Path,
        history_path: Path,
        ipy: bool = False,
    ) -> None:
        self.pyconfig_path = pyconfig_path
        self.history_path = history_path
        self.ipy = ipy

        self._pt: Optional["PythonInput"] = None

    def start(self, **kwargs: Any) -> None:
        """Start the pt(i)python Read-eval-print-loop.

        This uses the embed() methods provided by ptpython to start an instance
        in the running environment after doing all start-up work in lvim. Any
        keyword arguments provided will be made available in the namespace of
        the embedded interpreter. By default this is used to make some useful
        things global, such as the connected Nvim API client at `vim`.

        Currently none of the magics, notifications, or cwd/cd/pd management
        are implemented in the PyREPL. However, it can all be done via the
        Python API.
        """

        if self.ipy:
            self.start_ipython(**kwargs)
        else:
            self.start_python(**kwargs)

    def start_python(self, **kwargs: Any) -> None:
        """Start the ptpython REPL (--py).

        This is backed by ptpython.python_input.PythonInput, which provides a
        simple wrapper around eval()/exec() in the current process.
        """

        try:
            from ptpython.repl import embed as embed_python
        except ImportError:
            click.secho(
                "ptpython not found in Python environment",
                fg="yellow",
            )
            raise click.exceptions.Exit(1)

        logger.debug("Updating global environment")
        globals().update(kwargs)

        # Use ptpython, passing in the local env
        logger.debug("Starting (PT)Python")
        embed_python(
            globals(),
            locals(),
            configure=self.configure,
            history_filename=str(self.history_path),
        )

    def start_ipython(self, **kwargs: Any) -> None:
        """Start the ptipython REPL (--ipy).

        This is backed by the IPython InteractiveShellEmbed wrapped with ptpython
        functionality.

        Raises:
            ImportError: If IPython cannot be imported.
        """

        logger.debug("Updating global environment")
        globals().update(kwargs)

        try:
            import IPython  # noqa: F401
        except ImportError:
            click.secho(
                "IPython not found in Python environment, install or use --py",
                fg="yellow",
            )
            raise click.exceptions.Exit(1)

        try:
            from ptpython.ipython import embed as embed_ipython
        except ImportError:
            click.secho(
                "ptpython not found in Python environment",
                fg="yellow",
            )
            raise click.exceptions.Exit(1)

        # IPython available, use ptipython, which "inherits" the local env
        logger.debug("Starting (PT)IPython")
        embed_ipython(configure=self.configure, history_filename=str(self.history_path))

    @property
    def pt(self) -> "PythonInput":
        """Reference to the current ptpython REPL instance.

        For IPython, this is a ptpython.ipython.IPythonInput
        For Python, this is a ptpython.repl.PythonRepl
        """

        if self._pt is None:
            raise ValueError("Prompt Toolkit REPL not created yet")

        return self._pt

    @pt.setter
    def pt(self, repl: "PythonInput") -> None:
        self._pt = repl

    def configure(self, repl: "PythonInput") -> None:
        """Configure the REPL.

        This is passed as the configure kwarg to the pt(i)python REPL and uses
        the run_config function used by the ptipython/ptpython entrypoints:
        https://github.com/prompt-toolkit/ptpython/blob/836431ff6775aac2c2e3aafa3295b259ebe99d0a/src/ptpython/repl.py#L453

        This will load the lvim config file at the path given and call the
        configure() function defined within it, passing a reference to the REPL
        itself in order to allow for changing overall config.

        Args:
            repl: PythonInput. Reference to the REPL instance being configured.
                  For IPython, this is a ptpython.ipython.IPythonInput
                  For Python, this is a ptpython.repl.PythonRepl
        """

        from lvim.pydefaults import LvimPrompt
        from ptpython.repl import run_config

        self.pt = repl
        self.pt.all_prompt_styles["lvim"] = LvimPrompt(repl)

        # TODO: Right now click.get_current_context() is having issues with the
        # threading config of normal --py
        self.pt.prompt_style = "lvim" if self.ipy else "classic"

        if self.pyconfig_path.exists():
            logger.debug(f"Running lvim pyconfig file at {self.pyconfig_path}")
            run_config(repl, str(self.pyconfig_path))

            # ptipython's embed overwrites the prompt_style back to ipython after
            # running configure, so this just swaps out the ipython definition
            # for the user provided one in the config if there is one
            # https://github.com/prompt-toolkit/ptpython/blob/836431ff6775aac2c2e3aafa3295b259ebe99d0a/src/ptpython/ipython.py#L257
            if self.ipy and repl.prompt_style != "ipython":
                if style := repl.all_prompt_styles.get(repl.prompt_style, None):
                    repl.all_prompt_styles["ipython"] = style
                    repl.prompt_style = "ipython"
        else:
            logger.debug(f"No lvim pyconfig file at {self.pyconfig_path}")
