import warnings

warnings.warn(
    "This package 'paddle-sdk' is deprecated and replaced by 'paddle.py'. Please use 'paddle.py' instead: https://pypi.org/project/paddle.py/",
    DeprecationWarning,
    stacklevel=2,
)

__version__ = "0.1.5"
__all__ = ["Client", "Environment"]

from .client import Client
from .environment import Environment