# MCP System Bridge

An implementation of the Model Context Protocol (MCP), acting as a simple bridge to native OS functionalities like clipboard management and URL handling.

## Getting Started

Here's an example configuration using `uvx` as the command runner:

```json
{
  "mcpServers": {
    "mcp-sys-bridge": {
      "command": "uvx",
      "args": [
        "mcp-sys-bridge"
      ]
    }
  }
}
```

To install the `uvx` refer to the [uv documentation](https://docs.astral.sh/uv/getting-started/installation).

## Available Tools

- `open_urls`: Open a list of URLs in the default browser.
- `copy_to_clipboard`: Copy text to the clipboard.
- `get_current_date_info`: Get comprehensive information about the current date including day, month, year, day of year, day name, leap year status, week number, and more.

## Changelog

### 0.1.4

- Defined annotations to declare tools as read-only.

### 0.1.3

- Added `get_current_date_info` tool to get comprehensive information about the current date.

### 0.1.2

- Change `open_url` to `open_urls` to open a list of URLs in the default browser.

### 0.1.1

- Improve the `open_url` tool to handle URLs without a scheme and validate that the URL is valid.

### 0.1.0

- Added `open_url` tool.
- Added `copy_to_clipboard` tool.

> If you find this project useful, please consider starring the repository. Contributions are welcome!
