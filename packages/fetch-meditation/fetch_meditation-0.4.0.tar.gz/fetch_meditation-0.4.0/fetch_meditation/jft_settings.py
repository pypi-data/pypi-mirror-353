"""
JFT Settings module.

This module defines the settings class for configuring JFT meditation fetchers.
"""

from dataclasses import dataclass
from fetch_meditation.jft_language import JftLanguage
from typing import Optional


@dataclass
class JftSettings:
    """
    Settings for JFT meditation fetchers.

    This class contains configuration parameters for fetching JFT meditations.

    Attributes:
        language (JftLanguage): The language to fetch meditations in
        time_zone (Optional[str]): The time zone to use for date calculations, or None for system default
    """

    language: JftLanguage
    time_zone: Optional[str] = None
