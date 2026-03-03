from enum import Enum

class CombinedValue:
    def __init__(self, value):
        self.value = value
    
    def __and__(self, other):
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")

class USABLE(str, Enum):
    ALL = "Everyone"
    SUDO = "Owner & Sudoers"
    OWNER = "Owner Only"
    BOT = "Bot Only"

    def __and__(self, other):
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")

class WORKS(str, Enum):
    ALL = "Anywhere"
    GROUP = "Groups Only"
    PRIVATE = "Private Only"
    CHANNEL = "Channels Only"

    def __and__(self, other):
        val2 = other.value if hasattr(other, "value") else str(other)
        return CombinedValue(f"{self.value} & {val2}")
