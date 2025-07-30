# Pylint MCP

An MCP server that runs pylint on a given file

## Features

- **lint**: Check a python file for syntactic errors using pylint.

## Prerequisites

- **Python**: Version 3.10 or greater
- **uv**: Package and dependency manager for Python projects.

## Installation

2. **Install Dependencies**:
   Add the required dependencies using `uv`:
   ```bash
   uv sync
   ```

## Usage

### Running the Server

Start the FastMCP server in development mode:
```bash
uv run mcp dev cli.py
```

### Installing to Claude Desktop

Install the server as a Claude Desktop application:
```bash
uv run mcp install cli.py --name "pylint"
```

Configuration file as a reference:

```json
{
   "mcpServers": {
       "pylint": {
           "command": "uvx",
           "args": [ "pylint-mcp" ]
       }
   }
}
```

### Available Tools

#### `lint`

Check a python file for syntactic errors using pylint.

**Parameters**:
- `filename` (str): The python source file to check for syntactic errors.

**Example**:
> Check `example.py` for syntactic errors

**Output**:
```
[
    {
        "type": "convention",
        "module": "example.cli",
        "obj": "",
        "line": 31,
        "column": 0,
        "endLine": null,
        "endColumn": null,
        "path": "example.py",
        "symbol": "line-too-long",
        "message": "Line too long (204/100)",
        "message-id": "C0301"
    },
    {
        "type": "error",
        "module": "example.cli",
        "obj": "",
        "line": 1,
        "column": 0,
        "endLine": 1,
        "endColumn": 17,
        "path": "example.py",
        "symbol": "import-error",
        "message": "Unable to import 'mcp'",
        "message-id": "E0401"
    }
]
```

## License

This project is licensed under the MIT License. See the [COPYING](COPYING) file for details.
