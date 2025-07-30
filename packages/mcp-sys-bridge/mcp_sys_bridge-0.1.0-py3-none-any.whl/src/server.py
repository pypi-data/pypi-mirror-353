import webbrowser

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
    try:
        webbrowser.open(url)
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
