from enum import Enum

class Feature(Enum):
    GENERAL = 'GENERAL'
    CODE_CHECK = 'CODE_CHECK'
    CODE_HELPER = 'CODE_HELPER'
    CS_CHATBOT = 'CS_CHATBOT'
    CODE_CHECK_FRONTEND = 'CODE_CHECK_FRONTEND'
    CODE_CHECK_BACKEND = 'CODE_CHECK_BACKEND'
    CODE_CHECK_APPS = 'CODE_CHECK_APPS'
    DOCUMENT_CHECKING = 'DOCUMENT_CHECKING'

    @classmethod
    def from_string(cls, feature_string: str):
        try:
            return cls[feature_string.upper()]
        except KeyError:
            return cls.GENERAL  # Default to GENERAL if not found
