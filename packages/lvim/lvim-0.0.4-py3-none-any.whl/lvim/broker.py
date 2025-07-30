#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager
from logging import Logger, getLogger
from typing import Any, Generator, Optional

from lvim.notifications import handle_notification
from lvim.session import NvimSession
from pynvim import Nvim

logger: Logger = getLogger(__name__)


class NvimBroker:
    """Nvim message "broker"

    This is a secondary Nvim API client that is connected by default when lvim
    is started. Instead of being exposed in the REPL as `vim` for interactive
    use, this one starts the RPC event loop, which establishes a persistent
    connection to the nvim server.

    With this connection, notifications can be sent back to the lvim client via
    nvim's rpcnotify method:
    aemiller@nvim://|⇒ vim.fn.rpcnotify(0, "lvim_ping")
    1
    pong

    Or in nvim itself:
    :lua vim.fn.rpcnotify(0, "lvim_ping")

    0 will notify all connected RPC clients. When an NvimBroker receives one,
    it will look up the corresponding notification handler and execute it with
    any arguments provided. See the notifications module for more info.

    TODO: Add a lua client for interacting with the broker in nvim.

    Args:
        parent: NvimSession. A connected parent session to the nvim server, which
            will be cloned to create the broker session.
        debug: bool. Enable additional debug behavior and output.

    Public Attributes:
        channel_id: int. ID assigned to the broker session, which can be used as
            the first argument to rpcnotify() in order to specifically notify
            this broker instance.
        session: NvimSession. Broker nvim session.
    """

    def __init__(self, parent: NvimSession, debug: bool = False) -> None:
        self.debug = debug
        self._parent: NvimSession = parent
        self._future: Optional[Future] = None
        self._executor: Optional[ThreadPoolExecutor] = None

        self._session: Optional[NvimSession] = None

    def handle_notification(self, name: str, *args: Any) -> None:
        """Handle a notification received by the broker.

        See the notifications module for current notifications.

        Args:
            name: str. Notification name.
        """

        handle_notification(self, name, *args)

    # The behavior here will differ between embedded and non-embedded, it needs
    # to be two entirely separate Nvim objects, but both connected to the same
    # instance
    @contextmanager
    def attach(self) -> Generator[NvimBroker, None, None]:
        """Create an NvimSession for the broker and connect it.

        This is a continuation of the attach logic in NvimSession, which will
        additionally spawn a second thread that will enter the session's
        run_loop() RPC event loop. At this point the broker is able to receive
        notifications and is yielded.

        On exit, the thread is cleanly stopped by issuing the special
        `lvim_broker_shutdown` notification over the RPC channel.
        """

        logger.debug("Entering broker session context")
        broker_session = self._parent.clone()

        # By default, don't log when the broker attaches, unless in --debug
        broker_session.hide_header = not self.debug
        # Notify can't be used for the broker since it is not in the main thread
        broker_session.hide_notify = True
        with (
            broker_session.attach() as session,
            ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="BrokerThread"
            ) as executor,
        ):
            try:
                self.session = session

                logger.debug("Starting nvim broker loop thread")
                self._executor = executor
                self._future = executor.submit(
                    self.session.vim.run_loop, None, self.handle_notification
                )

                yield self
            finally:
                logger.debug("Stopping nvim broker")

                if self.session is not None:
                    # This must be done with the parent Nvim instance, since it
                    # is in the main thread
                    self.vim.funcs.rpcnotify(
                        self.session.vim.channel_id, "lvim_broker_shutdown", True
                    )

    @property
    def channel_id(self) -> int:
        """RPC channel ID of this broker in nvim."""

        return self.session.vim.channel_id

    @property
    def session(self) -> NvimSession:
        """Connected broker NvimSession instance."""

        if not self._session:
            raise ValueError("Broker session is not connected")

        return self._session

    @session.setter
    def session(self, session: NvimSession) -> None:
        self._session = session

    @property
    def vim(self) -> Nvim:
        """Parent session connected Nvim API client.

        This is an alias to the vim attribute on the parent NvimSession, as the
        client for the broker session cannot be used while the event loop is
        running in another thread.
        """

        return self._parent.vim
