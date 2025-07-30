"""
Default image embedding provider.
"""

__all__ = ["Local"]

from .clip import Clip


class Local(Clip):
    pass
