#!/usr/bin/env python3
"""
MDict MCP Server

This server provides dictionary lookup functionality for LLMs using MDict files.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import click
from mcp.server import Server
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import BaseModel

from .dictionary import DictionaryManager


class MCPServerConfig(BaseModel):
    """Configuration for the MCP server."""
    
    dictionary_paths: List[Path] = []
    dictionary_dir: Optional[Path] = None
    log_level: str = "INFO"


class MDictMCPServer:
    """MDict MCP Server implementation."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.dictionary_manager = DictionaryManager()
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, config.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    async def initialize(self) -> None:
        """Initialize the server and load dictionaries."""
        self.logger.info("Initializing MDict MCP Server")
        
        # Load dictionaries
        for dict_path in self.config.dictionary_paths:
            try:
                await self.dictionary_manager.load_dictionary(dict_path)
                self.logger.info(f"Loaded dictionary: {dict_path}")
            except Exception as e:
                self.logger.error(f"Failed to load dictionary {dict_path}: {e}")
    
    def get_available_tools(self) -> List[Tool]:
        """Get list of available tools."""
        return [
            Tool(
                name="lookup_word",
                description="Look up a word in the loaded dictionaries",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "The word to look up"
                        },
                        "dictionary": {
                            "type": "string",
                            "description": "Optional specific dictionary name",
                            "default": None
                        }
                    },
                    "required": ["word"]
                }
            ),
            Tool(
                name="search_words",
                description="Search for words matching a pattern",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern or prefix"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        },
                        "dictionary": {
                            "type": "string",
                            "description": "Optional specific dictionary name",
                            "default": None
                        }
                    },
                    "required": ["pattern"]
                }
            ),
            Tool(
                name="list_dictionaries",
                description="List all loaded dictionaries with their metadata",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            Tool(
                name="scan_dictionaries",
                description="Scan the dictionary directory for new MDX files and load them",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            Tool(
                name="get_dictionary_metadata",
                description="Get detailed metadata information for a specific dictionary",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dictionary": {
                            "type": "string",
                            "description": "Dictionary name to get metadata for"
                        }
                    },
                    "required": ["dictionary"]
                }
            ),
            Tool(
                name="get_dictionary_keys",
                description="Get all available keys (words) from a dictionary or sample of keys",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dictionary": {
                            "type": "string",
                            "description": "Dictionary name to get keys from"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of keys to return (default: 100)",
                            "default": 100
                        },
                        "prefix": {
                            "type": "string",
                            "description": "Optional prefix to filter keys",
                            "default": None
                        }
                    },
                    "required": ["dictionary"]
                }
            ),
            Tool(
                name="find_similar_words",
                description="Find words similar to a given word using fuzzy matching",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "Word to find similar matches for"
                        },
                        "dictionary": {
                            "type": "string",
                            "description": "Optional specific dictionary name",
                            "default": None
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of similar words to return",
                            "default": 10
                        },
                        "max_distance": {
                            "type": "integer",
                            "description": "Maximum edit distance for similarity (1-3)",
                            "default": 2
                        }
                    },
                    "required": ["word"]
                }
            )
        ]
    
    async def handle_tool_call(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool call requests."""
        try:
            if request.params.name == "lookup_word":
                return await self._handle_lookup_word(request.params.arguments)
            elif request.params.name == "search_words":
                return await self._handle_search_words(request.params.arguments)
            elif request.params.name == "list_dictionaries":
                return await self._handle_list_dictionaries(request.params.arguments)
            elif request.params.name == "scan_dictionaries":
                return await self._handle_scan_dictionaries(request.params.arguments)
            elif request.params.name == "get_dictionary_metadata":
                return await self._handle_get_dictionary_metadata(request.params.arguments)
            elif request.params.name == "get_dictionary_keys":
                return await self._handle_get_dictionary_keys(request.params.arguments)
            elif request.params.name == "find_similar_words":
                return await self._handle_find_similar_words(request.params.arguments)
            else:
                raise ValueError(f"Unknown tool: {request.params.name}")
        
        except Exception as e:
            self.logger.error(f"Error handling tool call {request.params.name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True
            )
    
    async def _handle_lookup_word(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle word lookup."""
        word = arguments.get("word", "").strip()
        dictionary = arguments.get("dictionary")
        
        if not word:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": "Word cannot be empty",
                    "success": False
                }))],
                isError=True
            )
        
        try:
            result = await self.dictionary_manager.lookup_word(word, dictionary)
            
            response = {
                "word": word,
                "found": bool(result),
                "dictionary": dictionary,
                "definition": result if result else None,
                "success": True
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "word": word,
                    "success": False
                }))],
                isError=True
            )
    
    async def _handle_search_words(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle word search."""
        pattern = arguments.get("pattern", "").strip()
        limit = arguments.get("limit", 10)
        dictionary = arguments.get("dictionary")
        
        if not pattern:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": "Search pattern cannot be empty",
                    "success": False
                }))],
                isError=True
            )
        
        try:
            results = await self.dictionary_manager.search_words(pattern, limit, dictionary)
            
            response = {
                "pattern": pattern,
                "limit": limit,
                "dictionary": dictionary,
                "count": len(results),
                "words": results,
                "success": True
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "pattern": pattern,
                    "dictionary": dictionary,
                    "success": False
                }))],
                isError=True
            )
    
    async def _handle_list_dictionaries(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle dictionary listing."""
        try:
            dictionaries = await self.dictionary_manager.list_dictionaries()
            
            response = {
                "count": len(dictionaries),
                "dictionaries": dictionaries,
                "success": True
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "success": False
                }))],
                isError=True
            )

    async def _handle_scan_dictionaries(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle dictionary directory scanning."""
        try:
            if not self.config.dictionary_dir:
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "error": "No dictionary directory configured",
                        "success": False
                    }))],
                    isError=True
                )
            
            # Get currently loaded dictionaries
            current_dicts = await self.dictionary_manager.list_dictionaries()
            current_paths = {Path(d['path']) for d in current_dicts}
            
            # Scan directory for MDX files
            dictionary_dir = self.config.dictionary_dir
            mdx_files = list(dictionary_dir.glob("*.mdx"))
            
            if not mdx_files:
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "directory": str(dictionary_dir),
                        "total_files": 0,
                        "message": "No MDX files found",
                        "success": True
                    }, ensure_ascii=False, indent=2))]
                )
            
            # Find new dictionaries to load
            new_files = [f for f in mdx_files if f not in current_paths]
            
            if not new_files:
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "directory": str(dictionary_dir),
                        "total_files": len(mdx_files),
                        "already_loaded": len(mdx_files),
                        "new_loaded": 0,
                        "message": "No new dictionaries found. All MDX files are already loaded.",
                        "success": True
                    }, ensure_ascii=False, indent=2))]
                )
            
            # Load new dictionaries
            loaded_count = 0
            failed_files = []
            successfully_loaded = []
            
            for dict_path in new_files:
                try:
                    await self.dictionary_manager.load_dictionary(dict_path)
                    self.logger.info(f"Loaded new dictionary: {dict_path}")
                    loaded_count += 1
                    successfully_loaded.append(str(dict_path))
                except Exception as e:
                    self.logger.error(f"Failed to load dictionary {dict_path}: {e}")
                    failed_files.append({
                        "path": str(dict_path),
                        "name": dict_path.name,
                        "error": str(e)
                    })
            
            # Prepare response
            response = {
                "directory": str(dictionary_dir),
                "total_files": len(mdx_files),
                "already_loaded": len(mdx_files) - len(new_files),
                "new_loaded": loaded_count,
                "failed": len(failed_files),
                "successfully_loaded": successfully_loaded,
                "failed_files": failed_files,
                "success": True
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "success": False
                }))],
                isError=True
            )

    async def _handle_get_dictionary_metadata(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle getting detailed metadata for a specific dictionary."""
        dictionary = arguments.get("dictionary", "").strip()
        
        if not dictionary:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": "Dictionary name cannot be empty",
                    "success": False
                }))],
                isError=True
            )
        
        try:
            # Check if dictionary exists
            if dictionary not in self.dictionary_manager.dictionaries:
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "error": f"Dictionary '{dictionary}' not found",
                        "available_dictionaries": list(self.dictionary_manager.dictionaries.keys()),
                        "success": False
                    }))],
                    isError=True
                )
            
            dict_info = self.dictionary_manager.dictionaries[dictionary]
            metadata = dict_info.get_metadata()
            
            response = {
                "dictionary": dictionary,
                "metadata": metadata,
                "success": True
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "dictionary": dictionary,
                    "success": False
                }))],
                isError=True
            )

    async def _handle_get_dictionary_keys(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle getting keys from a dictionary."""
        dictionary = arguments.get("dictionary", "").strip()
        limit = arguments.get("limit", 100)
        prefix = arguments.get("prefix", "").strip() if arguments.get("prefix") else None
        
        if not dictionary:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": "Dictionary name cannot be empty",
                    "success": False
                }))],
                isError=True
            )
        
        try:
            # Check if dictionary exists
            if dictionary not in self.dictionary_manager.dictionaries:
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "error": f"Dictionary '{dictionary}' not found",
                        "available_dictionaries": list(self.dictionary_manager.dictionaries.keys()),
                        "success": False
                    }))],
                    isError=True
                )
            
            dict_info = self.dictionary_manager.dictionaries[dictionary]
            all_keys = await dict_info.get_keys()
            
            # Filter by prefix if provided
            if prefix:
                filtered_keys = [key for key in all_keys if key.lower().startswith(prefix.lower())]
            else:
                filtered_keys = list(all_keys)
            
            # Sort and limit results
            filtered_keys.sort()
            limited_keys = filtered_keys[:limit]
            
            response = {
                "dictionary": dictionary,
                "prefix": prefix,
                "total_keys": len(all_keys),
                "filtered_keys": len(filtered_keys),
                "returned_keys": len(limited_keys),
                "limit": limit,
                "keys": limited_keys,
                "success": True
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "dictionary": dictionary,
                    "success": False
                }))],
                isError=True
            )

    async def _handle_find_similar_words(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle finding similar words using fuzzy matching."""
        word = arguments.get("word", "").strip()
        dictionary = arguments.get("dictionary")
        limit = arguments.get("limit", 10)
        max_distance = arguments.get("max_distance", 2)
        
        if not word:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": "Word cannot be empty",
                    "success": False
                }))],
                isError=True
            )
        
        try:
            # Get available dictionaries
            target_dictionaries = []
            if dictionary:
                if dictionary not in self.dictionary_manager.dictionaries:
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps({
                            "error": f"Dictionary '{dictionary}' not found",
                            "available_dictionaries": list(self.dictionary_manager.dictionaries.keys()),
                            "success": False
                        }))],
                        isError=True
                    )
                target_dictionaries = [self.dictionary_manager.dictionaries[dictionary]]
            else:
                target_dictionaries = list(self.dictionary_manager.dictionaries.values())
            
            if not target_dictionaries:
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "error": "No dictionaries loaded",
                        "success": False
                    }))],
                    isError=True
                )
            
            # Find similar words
            similar_words = []
            word_lower = word.lower()
            
            for dict_info in target_dictionaries:
                try:
                    keys = await dict_info.get_keys()
                    
                    # Calculate similarity scores
                    for key in keys:
                        key_lower = key.lower()
                        distance = self._calculate_edit_distance(word_lower, key_lower)
                        
                        if distance <= max_distance:
                            similar_words.append({
                                "word": key,
                                "dictionary": dict_info.name,
                                "edit_distance": distance,
                                "similarity_score": 1.0 - (distance / max(len(word), len(key)))
                            })
                        
                        # Early exit if we have enough candidates
                        if len(similar_words) >= limit * 3:  # Get more candidates for better sorting
                            break
                    
                except Exception as e:
                    self.logger.warning(f"Error processing dictionary {dict_info.name}: {e}")
            
            # Sort by similarity score (higher is better) and edit distance (lower is better)
            similar_words.sort(key=lambda x: (-x["similarity_score"], x["edit_distance"]))
            
            # Limit results
            limited_results = similar_words[:limit]
            
            response = {
                "word": word,
                "dictionary": dictionary,
                "limit": limit,
                "max_distance": max_distance,
                "total_found": len(similar_words),
                "returned": len(limited_results),
                "similar_words": limited_results,
                "success": True
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "word": word,
                    "dictionary": dictionary,
                    "success": False
                }))],
                isError=True
            )

    def _calculate_edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._calculate_edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]


async def run_server(config: MCPServerConfig) -> None:
    """Run the MCP server."""
    mdict_server = MDictMCPServer(config)
    await mdict_server.initialize()
    
    server = Server("mdict-mcp")
    
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        return mdict_server.get_available_tools()
    
    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> Sequence[TextContent]:
        try:
            if name == "lookup_word":
                result = await mdict_server._handle_lookup_word(arguments or {})
            elif name == "search_words":
                result = await mdict_server._handle_search_words(arguments or {})
            elif name == "list_dictionaries":
                result = await mdict_server._handle_list_dictionaries(arguments or {})
            elif name == "scan_dictionaries":
                result = await mdict_server._handle_scan_dictionaries(arguments or {})
            elif name == "get_dictionary_metadata":
                result = await mdict_server._handle_get_dictionary_metadata(arguments or {})
            elif name == "get_dictionary_keys":
                result = await mdict_server._handle_get_dictionary_keys(arguments or {})
            elif name == "find_similar_words":
                result = await mdict_server._handle_find_similar_words(arguments or {})
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            return result.content
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mdict-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


@click.command()
@click.option(
    "--dictionary-dir", "-d",
    default="./mdicts",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Path to directory containing MDX dictionary files (default: ./mdicts)"
)
@click.option(
    "--log-level", "-l",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Log level"
)
def main(dictionary_dir: Path, log_level: str) -> None:
    """Start the MDict MCP Server."""
    
    # Find all MDX files in the specified directory
    dictionary_files = list(dictionary_dir.glob("*.mdx"))
    
    if not dictionary_files:
        click.echo(f"No MDX dictionary files found in {dictionary_dir}")
        return
    
    click.echo(f"Found {len(dictionary_files)} dictionaries in {dictionary_dir}")
    
    config = MCPServerConfig(
        dictionary_paths=dictionary_files,
        dictionary_dir=dictionary_dir,
        log_level=log_level
    )
    
    click.echo(f"Starting MDict MCP Server with {len(config.dictionary_paths)} dictionaries...")
    for dict_path in config.dictionary_paths:
        click.echo(f"  - {dict_path}")
    
    try:
        asyncio.run(run_server(config))
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")
    except Exception as e:
        click.echo(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main() 