#!/usr/bin/env python3
from lvim.defaults import get_prompt
from prompt_toolkit.formatted_text import AnyFormattedText
from ptpython.prompt_style import PromptStyle
from ptpython.python_input import PythonInput


class LvimPrompt(PromptStyle):
    """
    A prompt resembling the IPython prompt, used as the default prompt for the
    Python-based REPLs when lvim is run with --ipy
    """

    def __init__(self, python_input: PythonInput) -> None:
        self.python_input = python_input

    def in_prompt(self) -> AnyFormattedText:
        return get_prompt()

    def in2_prompt(self, width: int) -> AnyFormattedText:
        return [("class:in", "...: ".rjust(width))]

    def out_prompt(self) -> AnyFormattedText:
        return [
            ("class:out", "Out["),
            ("class:out.number", f"{self.python_input.current_statement_index}"),
            ("class:out", "]:"),
            ("", " "),
        ]
