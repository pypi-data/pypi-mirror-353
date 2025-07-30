# MDict MCP Server


Config for Claude Desktop:

```
{
  "mcpServers": {
    "mdict": {
      "command": "uvx",
      "args": [
        "mdict-mcp",
        "-d",
        "/path/to/mdicts/"
      ],
      "env": {
        "MDICT_DICTIONARY_DIR": "/path/to/mdicts/"
      }
    }
  }
}

```

Config for ChatWise:

```
# type stdio
# env MDICT_DICTIONARY_DIR=/path/to/mdicts/
uvx mdict-mcp
```

Available Tools: [TOOLS.md](./TOOLS.md)


Dependencies: 

- mcp
- mdict-utils


Local testing:

```bash
uv --directory $HOME/Developer/mdict-mcp run mdict-mcp --log-level INFO --dictionary-dir /path/to/mdicts/
```
