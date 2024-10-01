from enum import Enum, auto


class Feature(Enum):
    GENERAL = auto()
    CODE_CHECK = auto()
    CODE_HELPER = auto()
    CS_CHATBOT = auto()

    @classmethod
    def from_string(cls, feature_string: str):
        try:
            return cls[feature_string.upper()]
        except KeyError:
            return cls.GENERAL  # Default to GENERAL if not found
