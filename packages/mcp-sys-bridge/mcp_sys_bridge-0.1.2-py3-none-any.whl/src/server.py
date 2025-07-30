import webbrowser
from urllib.parse import urlparse, urlunparse

import pyperclip
from fastmcp import FastMCP

mcp = FastMCP(
    name="MCP System Bridge",
    instructions="This server provides tools for managing the system.",
)


@mcp.tool()
def open_urls(urls: list[str]) -> dict[str, str]:
    """
    Open a list of URLs in the default browser.
    """
    results = {}
    for url in urls:
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            parsed_url = urlparse(f"https://{url}")
        if not parsed_url.netloc:
            results[url] = "Error: Invalid URL. Please provide a valid URL."
            continue
        processed_url = urlunparse(parsed_url)
        try:
            webbrowser.open(processed_url)
            results[url] = "URL opened successfully."
        except Exception as e:
            results[url] = f"Error opening URL: {e}"
    return results


@mcp.tool()
def copy_to_clipboard(text: str) -> str:
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
