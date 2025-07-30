#!/usr/bin/env python3
"""lvim notification handlers.

A notification is a function which is executed when the NvimBroker for a given
lvim instance receives a notification with the same name, for example, in nvim:
:lua vim.fn.rpcnotify(0, "lvim_ping")

Will trigger the word "pong" to be printed in the lvim REPL.

Notification functions receive a reference to the NvimBroker that received them,
as well as any other arguments provided to rpcnotify(). They cannot return
anything directly, but can have other side effects within lvim itself.

TODO: Define a set of actual possible input/output lua values for RPC, since it
      is inherently already limited to a small set of things.
TODO: Improve the display of notifications using some of prompt toolkit's UI.
"""

from __future__ import annotations

from logging import Logger, getLogger
from typing import TYPE_CHECKING, Callable, Dict, TypeAlias

from click import secho

if TYPE_CHECKING:
    from lvim.broker import NvimBroker

    NotiFn: TypeAlias = Callable[[NvimBroker, str], None]

logger: Logger = getLogger(__name__)


def handle_notification(broker: NvimBroker, name: str, *args: str) -> None:
    """Handle a notification.

    This is used by the method of the same name on the NvimBroker and dispatches
    the notification to the registered handler function, if one exists.

    Args:
        broker: NvimBroker. The broker which received this notification.
        name: str. Name of the notification received.
    """

    if func := _HANDLERS.get(name, None):
        return func(broker, *args)
    else:
        secho(f"No handler defined for notification {name}", fg="red")


def broker_shutdown(broker: NvimBroker, *args: str) -> None:
    """Shut down the broker event loop and thread.

    This is sent by the NvimBroker itself when exiting the context in order to
    start a clean shutdown.
    """

    logger.debug("Got shutdown notification, stopping broker thread")

    # This handler is wrapped in an except Exception, so an interrupt
    # is needed to get around it
    raise KeyboardInterrupt()


def ping(broker: NvimBroker, *args: str) -> None:
    """Print "pong" in the lvim environment."""

    secho("pong", fg="green")


_HANDLERS: Dict[str, NotiFn] = {
    "lvim_broker_shutdown": broker_shutdown,
    "lvim_ping": ping,
}
