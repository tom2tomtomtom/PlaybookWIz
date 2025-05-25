"""Logging configuration using structlog."""

from __future__ import annotations

import logging
import sys
from typing import Literal

import structlog


def setup_logging(
    level: str = "INFO", fmt: Literal["json", "console"] = "json"
) -> None:
    """Configure structured logging.

    Parameters
    ----------
    level:
        Logging level (e.g. ``"INFO"`` or ``"DEBUG"``).
    fmt:
        Output format, ``"json"`` for machine-readable logs or ``"console"`` for
        human readable output.
    """

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        stream=sys.stdout,
        format="%(message)s",
    )

    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
    ]

    if fmt == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        processors=processors,
    )
