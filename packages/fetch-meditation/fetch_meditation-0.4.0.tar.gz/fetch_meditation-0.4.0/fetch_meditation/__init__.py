"""
Fetch Meditation Package.

This package provides functionality to fetch daily meditations from various sources
in multiple languages. It supports Just For Today (JFT) and Spiritual Principle A Day (SPAD)
meditation formats.

Available modules:
- jft: JFT meditation fetcher factory
- jft_language: Language enumeration for JFT meditations
- jft_settings: Settings for JFT meditation fetchers
- jft_entry: Data structure for JFT meditation entries
- spad: SPAD meditation fetcher factory
- spad_language: Language enumeration for SPAD meditations
- spad_settings: Settings for SPAD meditation fetchers
- spad_entry: Data structure for SPAD meditation entries
"""

__version__ = "0.4.0"

from fetch_meditation.jft_language import JftLanguage
from fetch_meditation.jft_settings import JftSettings
from fetch_meditation.jft import Jft
from fetch_meditation.spad_language import SpadLanguage
from fetch_meditation.spad_settings import SpadSettings
from fetch_meditation.spad import Spad
