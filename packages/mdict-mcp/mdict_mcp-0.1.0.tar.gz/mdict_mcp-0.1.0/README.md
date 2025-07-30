# MDict MCP Server

## Installation

```bash
git clone https://github.com/cdpath/mdict-mcp
cd mdict-mcp
uv sync
```

## Usage

1. Place your MDX dictionary files in the `/path/to/mdicts/` directory
2. Start the MCP server:

```bash
uv run mdict-mcp -d /path/to/mdicts/
```

3. Connect from your MCP client (Claude Desktop, Chatwise, etc.)

Chatwise:

```
uv --directory $HOME/Developer/mdict-mcp run mdict-mcp --log-level INFO --dictionary-dir /path/to/mdicts/
```


## Available Tools

### Core Dictionary Tools

<details>
<summary><strong>lookup_word</strong> - Look up a word in the loaded dictionaries</summary>

**Request:**
```json
{
  "word": "science",
  "dictionary": "optional_specific_dictionary_name"
}
```

**Response:**
```json
{
  "word": "science",
  "found": true,
  "dictionary": null,
  "definition": "<HTML definition content>",
  "success": true
}
```
</details>

<details>
<summary><strong>search_words</strong> - Search for words matching a pattern</summary>

**Request:**
```json
{
  "pattern": "sci",
  "limit": 10,
  "dictionary": "optional_specific_dictionary_name"
}
```

**Response:**
```json
{
  "pattern": "sci",
  "limit": 10,
  "dictionary": null,
  "count": 5,
  "words": ["science", "scientist", "scissors", "scintillate", "scimitar"],
  "success": true
}
```
</details>

<details>
<summary><strong>find_similar_words</strong> - Find words similar to a given word using fuzzy matching</summary>

**Request:**
```json
{
  "word": "science",
  "dictionary": "optional_specific_dictionary_name",
  "limit": 10,
  "max_distance": 2
}
```

**Response:**
```json
{
  "word": "science",
  "dictionary": null,
  "limit": 10,
  "max_distance": 2,
  "total_found": 15,
  "returned": 10,
  "similar_words": [
    {
      "word": "sciences",
      "dictionary": "Webster",
      "edit_distance": 1,
      "similarity_score": 0.875
    }
  ],
  "success": true
}
```
</details>

### Dictionary Management Tools

<details>
<summary><strong>list_dictionaries</strong> - List all loaded dictionaries with metadata</summary>

**Request:**
```json
{}
```

**Response:**
```json
{
  "count": 2,
  "dictionaries": [
    {
      "name": "Webster",
      "path": "/path/to/webster.mdx",
      "description": "Webster's Dictionary",
      "version": "1.0"
    }
  ],
  "success": true
}
```
</details>

<details>
<summary><strong>scan_dictionaries</strong> - Scan the dictionary directory for new MDX files and load them</summary>

**Request:**
```json
{}
```

**Response:**
```json
{
  "directory": "./mdicts",
  "total_files": 5,
  "already_loaded": 2,
  "new_loaded": 3,
  "failed": 0,
  "successfully_loaded": ["./mdicts/oxford.mdx"],
  "failed_files": [],
  "success": true
}
```
</details>

<details>
<summary><strong>get_dictionary_metadata</strong> - Get detailed metadata information for a specific dictionary</summary>

**Request:**
```json
{
  "dictionary": "dictionary_name"
}
```

**Response:**
```json
{
  "dictionary": "Webster",
  "metadata": {
    "title": "Webster's Dictionary",
    "description": "English Dictionary",
    "version": "1.0",
    "entries": 50000
  },
  "success": true
}
```
</details>

<details>
<summary><strong>get_dictionary_keys</strong> - Get all available keys (words) from a dictionary or sample of keys</summary>

**Request:**
```json
{
  "dictionary": "dictionary_name",
  "limit": 100,
  "prefix": "optional_prefix"
}
```

**Response:**
```json
{
  "dictionary": "Webster",
  "prefix": "sci",
  "total_keys": 50000,
  "filtered_keys": 25,
  "returned_keys": 10,
  "limit": 10,
  "keys": ["science", "scientist", "scientific"],
  "success": true
}
```
</details>


### Dependencies

- mcp: Model Context Protocol implementation
- mdict-utils: MDX/MDD file parsing
