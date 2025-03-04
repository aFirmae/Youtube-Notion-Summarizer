import os
import re
import requests


class NotionClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def create_page(self, database_id, title, content, video_url=""):
        """Create a page in Notion database with the given title and content."""
        print(f"Created page '{title}' in Notion, now adding summary content...")

        # Create the page with title
        page_data = {
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": title}}]},
                "Video URL": {"url": video_url} if video_url else None,
            },
            "children": self._parse_markdown_to_blocks(content),
        }

        # Create the page
        response = requests.post(
            f"{self.base_url}/pages", headers=self.headers, json=page_data
        )

        if response.status_code != 200:
            raise Exception(f"Error creating Notion page: {response.text}")

        return response.json()

    def _parse_markdown_to_blocks(self, markdown_content):
        """Parse markdown content into Notion blocks"""
        blocks = []
        lines = markdown_content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Handle headings
            if line.startswith("# "):
                blocks.append(
                    {"heading_1": {"rich_text": [{"text": {"content": line[2:]}}]}}
                )
            elif line.startswith("## "):
                blocks.append(
                    {"heading_2": {"rich_text": [{"text": {"content": line[3:]}}]}}
                )
            elif line.startswith("### "):
                blocks.append(
                    {"heading_3": {"rich_text": [{"text": {"content": line[4:]}}]}}
                )

            # Handle bullet points with emojis and formatting
            elif line.startswith("- "):
                content = line[2:]  # Remove the "- " prefix

                # Process rich text features like bold
                rich_text_elements = self._process_rich_text(content)

                blocks.append({"bulleted_list_item": {"rich_text": rich_text_elements}})

            # Handle paragraphs (anything else)
            else:
                # Combine multiple lines into a single paragraph until we hit an empty line
                paragraph_text = line
                j = i + 1
                while (
                    j < len(lines)
                    and lines[j].strip()
                    and not (
                        lines[j].strip().startswith("#")
                        or lines[j].strip().startswith("-")
                    )
                ):
                    paragraph_text += " " + lines[j].strip()
                    j += 1
                    i += 1

                # Process rich text features like bold
                rich_text_elements = self._process_rich_text(paragraph_text)

                # Handle paragraph length limit (2000 chars)
                if len(paragraph_text) <= 2000:
                    blocks.append({"paragraph": {"rich_text": rich_text_elements}})
                else:
                    # Split into multiple paragraph blocks
                    chunks = [
                        paragraph_text[i : i + 1990]
                        for i in range(0, len(paragraph_text), 1990)
                    ]
                    for chunk in chunks:
                        blocks.append(
                            {"paragraph": {"rich_text": [{"text": {"content": chunk}}]}}
                        )

            i += 1

        return blocks

    def _process_rich_text(self, text):
        """Process text for bold, italic, etc. formatting"""
        # This is a simplified version - for proper parsing we'd need a full markdown parser
        rich_text = []

        # Check for bold text
        bold_pattern = r"\*\*(.*?)\*\*"
        matches = re.findall(bold_pattern, text)

        if matches:
            # Text has bold formatting
            parts = re.split(bold_pattern, text)
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Regular text
                    if part:
                        rich_text.append({"text": {"content": part}})
                else:  # Bold text
                    rich_text.append(
                        {"text": {"content": part}, "annotations": {"bold": True}}
                    )
        else:
            # No formatting, just plain text
            rich_text.append({"text": {"content": text}})

        return rich_text
