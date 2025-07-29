"""
JFT Entry module.

This module defines the data structure for JFT meditation entries.
"""

import json
from typing import Any, Dict, List
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class JftEntry:
    """
    Data class representing a JFT (Just For Today) meditation entry.

    This class holds all the components of a JFT meditation and provides
    methods for conversion to different formats.

    Attributes:
        date (str): The date of the meditation
        title (str): The title of the meditation
        page (str): The page reference
        quote (str): The quote text
        source (str): The source of the quote
        content (List[str]): The main content paragraphs
        thought (str): The closing thought
        copyright (str): Copyright information
    """

    date: str
    title: str
    page: str
    quote: str
    source: str
    content: List[str]
    thought: str
    copyright: str

    def _to_dict(self) -> Dict[str, Any]:
        """
        Convert the entry to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the entry
        """
        return {
            "date": self.date,
            "title": self.title,
            "page": self.page,
            "quote": self.quote,
            "source": self.source,
            "content": self.content,
            "thought": self.thought,
            "copyright": self.copyright,
        }

    def to_json(self) -> str:
        """
        Convert the entry to a JSON string.

        Returns:
            str: JSON string representation of the entry
        """
        return json.dumps(self._to_dict())

    def without_tags(self) -> Dict[str, Any]:
        """
        Create a version of the entry with HTML tags stripped.

        Returns:
            Dict[str, Any]: Dictionary with HTML tags removed from all values
        """

        def strip_tags(item: str) -> str:
            if isinstance(item, list):
                return [strip_tags(sub_item) for sub_item in item]
            else:
                soup = BeautifulSoup(item, "html.parser")
                return soup.text

        return {key: strip_tags(value) for key, value in self._to_dict().items()}
