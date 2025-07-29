"""
SPAD Settings module.

This module defines the settings class for configuring SPAD meditation fetchers.
"""

from dataclasses import dataclass
from fetch_meditation.spad_language import SpadLanguage
from typing import Optional


@dataclass
class SpadSettings:
    """
    Settings for SPAD meditation fetchers.

    This class contains configuration parameters for fetching SPAD meditations.

    Attributes:
        language (SpadLanguage): The language to fetch meditations in
        time_zone (Optional[str]): The time zone to use for date calculations, or None for system default
    """

    language: SpadLanguage
    time_zone: Optional[str] = None
