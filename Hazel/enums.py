from enum import Enum

class CombinedValue:
    def __init__(self, value):
        self.value = value
    
    def __and__(self, other):
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")

class USABLE(str, Enum):
    ALL = "Everyone"
    SUDO = "Sudoers"
    OWNER = "Owners"
    BOT = "Business Bots"

    def __and__(self, other):
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")

class WORKS(str, Enum):
    ALL = "Anywhere"
    GROUP = "Groups"
    PRIVATE = "Private"
    CHANNEL = "Channels"

    def __and__(self, other):
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")
