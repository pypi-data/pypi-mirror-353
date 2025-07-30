#!/usr/bin/env python3
from __future__ import annotations

from contextlib import contextmanager
from logging import Logger, getLogger
from pathlib import Path
from typing import Generator, Optional

from lvim.nvim import parent_nvim
from pynvim import Nvim

logger: Logger = getLogger(__name__)


class NvimSession:
    """A connected Nvim "session"

    This encapsulates the pynvim API client along with some session specific
    configuration and state.

    Args:
        connection: Optional[str]. Connection string. If not provided, lvim will
            attempt to look up a connection via $NVIM in the environment.
        hide_header: bool. If True, don't display the connection header in the
            lvim REPL.
        hide_notify: bool. If True, don't display the client attachment
            notification in the parent nvim instance.
        debug: bool. Enable additional debug behavior and output.

    Public Attributes:
        vim: Nvim. Connected Nvim API client.
    """

    def __init__(
        self,
        hide_header: bool = False,
        hide_notify: bool = False,
        connection: Optional[str] = None,
        debug: bool = False,
    ) -> None:
        self.hide_header = hide_header
        self.hide_notify = hide_notify
        self.connection = connection
        self.debug = debug

        self._vim: Optional[Nvim] = None

    def clone(self) -> NvimSession:
        """Clone an NvimSession.

        This creates a new session object with the same configuration. It will
        have a separate Nvim API client when connected.

        Returns:
            cloned: NvimSession. Cloned NvimSession instance.
        """

        return NvimSession(
            hide_header=self.hide_header, connection=self.connection, debug=self.debug
        )

    @contextmanager
    def attach(self) -> Generator[NvimSession, None, None]:
        """Attach the session to the configured nvim server.

        See parent_nvim for details on how the nvim instance is discovered.
        """

        logger.debug("Entering nvim session context")
        with parent_nvim(
            connection=self.connection,
            hide_header=self.hide_header,
            hide_notify=self.hide_notify,
        ) as nvim:
            try:
                # Store API client reference
                self.vim = nvim

                yield self
            finally:
                # Clear API client reference
                self._vim = None

    @property
    def vim(self) -> Nvim:
        """Session-local connected Nvim API client.

        Reference: https://pynvim.readthedocs.io/en/latest/api/nvim.html
        """

        if not self._vim:
            raise ValueError("Session is not connected")

        return self._vim

    @vim.setter
    def vim(self, session: Nvim) -> None:
        self._vim = session

    @property
    def cwd(self) -> Path:
        return self.vim.funcs.getcwd()
