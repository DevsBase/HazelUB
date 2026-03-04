from __future__ import annotations
from enum import Enum
from typing import Union, Any

class CombinedValue:
    """Holds a combined string value produced by ``&``-chaining enum members."""

    def __init__(self, value: str) -> None:
        """Initialise with the pre-formatted combined string."""
        self.value = value

    def __and__(self, other: Union[CombinedValue, USABLE, WORKS, Any]) -> CombinedValue:
        """Combine with another enum member or :class:`CombinedValue`.

        Args:
            other: Another :class:`USABLE`, :class:`WORKS`, or
                :class:`CombinedValue` instance to append.

        Returns:
            CombinedValue: A new instance whose ``.value`` is
                ``"<self.value> & <other.value>"``.
        """
        
        val2 = getattr(other, "value", str(other))
        return CombinedValue(f"{self.value} & {val2}")

    def __repr__(self) -> str:
        return f"CombinedValue(value={self.value!r})"


class USABLE(str, Enum):
    """Enum describing which user roles are permitted to use a module."""

    ALL = "Everyone"
    SUDO = "Sudoers"
    OWNER = "Owners"
    BOT = "Business Bots"

    def __and__(self, other: Union[CombinedValue, USABLE, Any]) -> CombinedValue:
        """Combine this member with another using ``&``."""
        val2 = getattr(other, "value", str(other))
        return CombinedValue(f"{self.value} & {val2}")


class WORKS(str, Enum):
    """Enum describing in which chat contexts a module functions."""

    ALL = "Anywhere"
    GROUP = "Groups"
    PRIVATE = "Private"
    CHANNEL = "Channels"

    def __and__(self, other: Union[CombinedValue, WORKS, Any]) -> CombinedValue:
        """Combine this member with another using ``&``."""
        val2 = getattr(other, "value", str(other))
        return CombinedValue(f"{self.value} & {val2}")