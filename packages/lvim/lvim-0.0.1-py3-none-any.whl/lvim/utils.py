#!/usr/bin/env python3
from __future__ import annotations

from logging import Logger, getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Tuple

from click import get_current_context

if TYPE_CHECKING:
    from lvim.context import Context

logger: Logger = getLogger(__name__)


def get_context() -> Context:
    return get_current_context().obj


def get_cwd() -> Path:
    context = get_context()
    return context.cwd


def set_cwd(path: Path) -> Path:
    context = get_context()
    context.set_cwd(path)

    return context.cwd


def update_cwd() -> None:
    context = get_context()
    context.update_cwd()


def get_cd() -> Path:
    context = get_context()
    return context.cd


def set_cd(path: Path) -> Path:
    context = get_context()
    context.set_cd(path)

    return context.cd


def update_cd() -> None:
    context = get_context()
    context.update_cd()


def get_pd() -> Path:
    context = get_context()
    return context.pd


def set_pd(path: Path) -> Path:
    context = get_context()
    context.set_pd(path)

    return context.pd


def format_path() -> Tuple[str, bool]:
    # TODO: // should probably be broken out into some generic "pinned" directory
    # functionality. // %cd! aecode resulting in just // is confusing
    cwd = get_cwd()
    logger.debug(f"Current vim cwd: {cwd}")
    cd = get_cd()
    logger.debug(f"Current lvim cd: {cd}")
    pd = get_pd()
    logger.debug(f"Current lvim pinned dir: {pd}")
    home = Path.home()

    paths_synced = cwd == cd

    if cd == home:
        formatted = "~/"
    elif pd == home and cd.is_relative_to(home):
        formatted = f"~/{cd.relative_to(home)}"
    elif cd == pd:
        formatted = "//"
    elif cd.is_relative_to(pd):
        formatted = f"//{cd.relative_to(pd)}"
    elif cd.is_relative_to(Path.home()):
        formatted = f"~/{cd.relative_to(home)}"
    else:
        # Otherwise use absolute path.
        formatted = str(cd)

    return str(formatted), paths_synced
