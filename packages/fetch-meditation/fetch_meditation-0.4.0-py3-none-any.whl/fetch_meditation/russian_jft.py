from typing import Dict, List, Any
import re
from bs4 import BeautifulSoup
from fetch_meditation.utilities.http_utility import HttpUtility
from fetch_meditation.jft_entry import JftEntry


class RussianJft:
    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def fetch(self) -> "JftEntry":
        url = "https://na-russia.org/meditation-today"
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

        # Extract date (e.g., "5 июня")
        date_elements = soup.find_all("div", class_=lambda x: x and "mt-4" in x and "text-md" in x)
        for element in date_elements:
            text = element.get_text(strip=True)
            if re.match(r"^\d+\s+\w+$", text):
                result["date"] = text
                break

        # Extract title (e.g., "Честная молитва")
        title_elements = soup.find_all("div", class_=lambda x: x and "font-bold" in x)
        if title_elements:
            result["title"] = title_elements[0].get_text(strip=True)

        # Extract quote (text in italics)
        quote_elements = soup.find_all("div", class_=lambda x: x and "italic" in x)
        if quote_elements:
            result["quote"] = quote_elements[0].get_text(strip=True)

        # Extract source (e.g., "Базовый текст, с. 120")
        source_elements = soup.find_all(
            "div", class_=lambda x: x and "text-secondary-blue" in x and "whitespace-nowrap" in x
        )
        if source_elements:
            result["source"] = source_elements[0].get_text(strip=True)

        # Extract main content
        content_elements = soup.find_all(
            "div", class_=lambda x: x and "mt-8" in x and "text-md" in x
        )
        if content_elements:
            content_element = content_elements[0]

            # Get the HTML content to process <br> tags
            content_html = str(content_element)

            # Split by <br> tags and filter out the "ТОЛЬКО СЕГОДНЯ:" part
            paragraphs = re.split(r"<br\s*/?>", content_html, flags=re.IGNORECASE)
            filtered_content = []

            for paragraph in paragraphs:
                # Remove HTML tags and clean text
                clean_text = BeautifulSoup(paragraph, "html.parser").get_text(strip=True)
                if clean_text and not re.match(r"^ТОЛЬКО СЕГОДНЯ:", clean_text):
                    filtered_content.append(clean_text)

            result["content"] = filtered_content

            # Extract "ТОЛЬКО СЕГОДНЯ" section
            full_text = content_element.get_text(strip=True)
            jft_match = re.search(r"ТОЛЬКО СЕГОДНЯ:\s*(.+)", full_text)
            if jft_match:
                result["thought"] = jft_match.group(1).strip()

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
