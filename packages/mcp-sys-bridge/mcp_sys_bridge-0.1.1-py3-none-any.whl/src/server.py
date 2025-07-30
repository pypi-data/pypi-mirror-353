import webbrowser
from urllib.parse import urlparse, urlunparse

import pyperclip
from fastmcp import FastMCP

mcp = FastMCP(
    name="MCP System Bridge",
    instructions="This server provides tools for managing the system.",
)


@mcp.tool()
async def open_url(url: str) -> str:
    """
    Open a URL in the default browser.
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        parsed_url = urlparse(f"https://{url}")
    if not parsed_url.netloc:
        return "Error: Invalid URL. Please provide a valid URL."
    processed_url = urlunparse(parsed_url)
    try:
        webbrowser.open(processed_url)
        return "URL opened successfully."
    except Exception as e:
        return f"Error opening URL: {e}"


@mcp.tool()
async def copy_to_clipboard(text: str) -> str:
    """
    Copy text to the clipboard.
    """
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard successfully."
    except Exception as e:
        return f"Error copying text to clipboard: {e}"


def main() -> None:
    mcp.run(transport="stdio")
