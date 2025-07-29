"""Terminal style package for formatting and styling terminal output.

This package provides utilities for adding colors, background colors, and text effects
to terminal output. It includes functions for both printing styled text and returning
styled strings.
"""

import datetime

from .spinner import spinner
from .terminal_style import sprint, style

__all__ = [
    "spinner",
    "sprint",
    "style",
]

__title__ = "terminal-style"
__version__ = "0.0.4"
__license__ = "MIT"

_this_year = datetime.datetime.now(tz=datetime.UTC).date().year
__copyright__ = f"Copyright {_this_year} Colin Frisch"
