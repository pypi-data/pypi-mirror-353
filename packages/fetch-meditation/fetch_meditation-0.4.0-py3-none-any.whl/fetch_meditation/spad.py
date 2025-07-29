"""
SPAD (Spiritual Principle A Day) meditation fetcher module.

This module provides functionality to fetch SPAD meditations in different languages.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
from fetch_meditation.spad_language import SpadLanguage
from fetch_meditation.english_spad import EnglishSpad


@dataclass
class Spad:
    """
    Main SPAD meditation fetcher class.

    This class serves as a factory for creating language-specific SPAD meditation fetchers
    based on the provided settings.

    Attributes:
        settings: Configuration settings for the SPAD fetcher
    """

    settings: Any

    def fetch(self) -> None:
        """
        Base fetch method, overridden in language-specific implementations.
        """
        pass

    @property
    def language(self) -> SpadLanguage:
        """
        Get the language setting for this SPAD fetcher.

        Returns:
            SpadLanguage: The language enum value
        """
        return self.settings.language

    @staticmethod
    def get_instance(settings: Any) -> EnglishSpad:
        """
        Factory method to create a language-specific SPAD fetcher.

        Args:
            settings: Configuration settings for the SPAD fetcher

        Returns:
            A language-specific SPAD fetcher instance
        """
        return {
            SpadLanguage.English: EnglishSpad,
        }[
            settings.language
        ](settings)
