from enum import Enum

class CombinedValue:
    """Holds a combined string value produced by ``&``-chaining enum members.

    Used as the result type when two :class:`USABLE` or :class:`WORKS` enum
    members are combined with the ``&`` operator.
    """

    def __init__(self, value: str) -> None:
        """Initialise with the pre-formatted combined string."""
        self.value = value

    def __and__(self, other: object) -> "CombinedValue":
        """Combine with another enum member or :class:`CombinedValue`.

        Args:
            other: Another :class:`USABLE`, :class:`WORKS`, or
                :class:`CombinedValue` instance to append.

        Returns:
            CombinedValue: A new instance whose ``.value`` is
            ``"<self.value> & <other.value>"``.
        """
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")

class USABLE(str, Enum):
    """Enum describing which user roles are permitted to use a module.

    Members
    -------
    ALL
        The command is usable by everyone.
    SUDO
        Only sudoers (and the account owner) may use the command.
    OWNER
        Restricted to the account owner only.
    BOT
        Restricted to business-bot mode.
    """

    ALL = "Everyone"
    SUDO = "Sudoers"
    OWNER = "Owners"
    BOT = "Business Bots"

    def __and__(self, other: object) -> CombinedValue:
        """Combine this member with another using ``&``.

        Args:
            other: Another :class:`USABLE` member or :class:`CombinedValue`.

        Returns:
            CombinedValue: A new combined value string.
        """
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")

class WORKS(str, Enum):
    """Enum describing in which chat contexts a module functions.

    Members
    -------
    ALL
        The command works in any chat type.
    GROUP
        Works only in groups and supergroups.
    PRIVATE
        Works only in private chats (DMs).
    CHANNEL
        Works only in channels.
    """

    ALL = "Anywhere"
    GROUP = "Groups"
    PRIVATE = "Private"
    CHANNEL = "Channels"

    def __and__(self, other: object) -> CombinedValue:
        """Combine this member with another using ``&``.

        Args:
            other: Another :class:`WORKS` member or :class:`CombinedValue`.

        Returns:
            CombinedValue: A new combined value string.
        """
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")
