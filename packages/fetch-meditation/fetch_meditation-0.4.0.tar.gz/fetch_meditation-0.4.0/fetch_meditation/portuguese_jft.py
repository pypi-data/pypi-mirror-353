from typing import Dict, List, Any
import re
from bs4 import BeautifulSoup
from fetch_meditation.utilities.http_utility import HttpUtility
from fetch_meditation.jft_entry import JftEntry


class PortugueseJft:
    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def fetch(self) -> "JftEntry":
        url = "https://na-pt.org/sph/"
        data = HttpUtility.http_get(url)
        soup = BeautifulSoup(data, "html.parser")

        result = {
            "date": "",
            "quote": "",
            "source": "",
            "thought": "",
            "content": [],
            "title": "",
            "page": "",
            "copyright": "",
        }

        # Extract date from qx-text-6112
        date_element = soup.find("div", id="qx-text-6112")
        if date_element:
            date_text = date_element.get_text(strip=True)
            # Extract just the date part, removing "MEDITAÇÃO DO DIA"
            # Look for pattern like "quinta, 04 de junho de 2025" but exclude "DIA" prefix
            date_match = re.search(
                r"(?:DIA)?([A-Za-z]+,\s*\d+\s+de\s+[A-Za-z]+\s+de\s+\d+)", date_text, re.IGNORECASE
            )
            if date_match:
                result["date"] = date_match.group(1).strip()

        # Extract title from h2 within qx-heading-5146
        title_element = soup.select_one("#qx-heading-5146 h2 span")
        if title_element:
            result["title"] = title_element.get_text(strip=True)

        # Extract main content from qx-text-39245
        content_element = soup.find("div", id="qx-text-39245")
        if content_element:
            # Get the full text content
            full_text = content_element.get_text(separator="\n", strip=True)

            # Extract the quote (text between quotes)
            quote_match = re.search(r'"([^"]+)"', full_text)
            if quote_match:
                result["quote"] = quote_match.group(1).strip()

            # Split into lines for processing
            lines = [line.strip() for line in full_text.split("\n") if line.strip()]

            # Find the source line (should be right after the quote)
            quote_found = False
            for i, line in enumerate(lines):
                if quote_match and quote_match.group(0) in line:
                    quote_found = True
                elif quote_found and line and not line.startswith('"'):
                    # This should be the source line
                    result["source"] = line
                    break

            # Extract the main content (everything after the source line)
            content_lines = []
            source_found = False

            for line in lines:
                # Skip the quote line
                if quote_match and quote_match.group(0) in line:
                    continue

                # Skip the source line
                if not source_found and result["source"] and line == result["source"]:
                    source_found = True
                    continue

                # Collect content after source
                if source_found and line:
                    content_lines.append(line)

            if content_lines:
                # Join all content lines into a single paragraph
                content_text = " ".join(content_lines)
                # Clean up multiple spaces
                cleaned_content = re.sub(r"\s+", " ", content_text).strip()
                result["content"] = [cleaned_content] if cleaned_content else []

        # Extract "SÓ POR HOJE" section from qx-text-80201
        sph_element = soup.find("div", id="qx-text-80201")
        if sph_element:
            sph_text = sph_element.get_text(strip=True)
            # Remove "SÓ POR HOJE:" prefix
            thought_match = re.sub(r"^SÓ POR HOJE:\s*", "", sph_text)
            result["thought"] = re.sub(r"\s+", " ", thought_match).strip()

        # Extract copyright from qx-text-28340
        copyright_element = soup.find("div", id="qx-text-28340")
        if copyright_element:
            # Use separator to preserve line breaks as spaces
            copyright_text = copyright_element.get_text(separator=" ", strip=True)
            result["copyright"] = re.sub(r"\s+", " ", copyright_text).strip()

        result["page"] = ""

        return JftEntry(
            result["date"],
            result["title"],
            result["page"],
            result["quote"],
            result["source"],
            result["content"],
            result["thought"],
            result["copyright"],
        )
