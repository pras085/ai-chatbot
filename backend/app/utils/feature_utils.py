from enum import Enum, auto


class Feature(Enum):
    GENERAL = 'GENERAL'
    CODE_CHECK = 'CODE_CHECK'
    CODE_HELPER = 'CODE_HELPER'
    CS_CHATBOT = 'CS_CHATBOT'

    @classmethod
    def from_string(cls, feature_string: str):
        try:
            return cls[feature_string.upper()]
        except KeyError:
            return cls.GENERAL  # Default to GENERAL if not found
