"""
JFT Language enumeration module.

This module defines the available languages for JFT (Just For Today) meditations.
"""

from enum import Enum


class JftLanguage(Enum):
    """
    Enumeration of supported languages for JFT meditations.

    Each enum value represents a language for which JFT meditations can be fetched.
    """

    English = 1
    French = 2
    German = 3
    Italian = 4
    Japanese = 5
    Portuguese = 6
    Russian = 7
    Spanish = 8
    Swedish = 9
