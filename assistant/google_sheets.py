import re


def extract_sheet_key(link: str) -> str | None:
    """Extract the Google Sheet key from a full URL.

    Returns the key found between ``spreadsheets/d/`` and the next ``/``.
    """
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", link)
    if match:
        return match.group(1)
    return None
