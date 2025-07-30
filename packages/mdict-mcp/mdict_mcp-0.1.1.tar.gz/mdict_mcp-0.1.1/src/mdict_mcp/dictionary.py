"""
Dictionary management module for MDict files.

This module handles loading, querying, and searching MDict dictionaries.
"""

import asyncio
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import logging

from mdict_utils.reader import MDX, MDD, query, get_keys, meta


class DictionaryInfo:
    """Information about a loaded dictionary."""
    
    def __init__(self, name: str, path: Path, metadata: Dict[str, Any]):
        self.name = name
        self.path = path
        self.metadata = metadata
        self._keys_cache: Optional[Set[str]] = None
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get dictionary metadata."""
        return {
            "name": self.name,
            "path": str(self.path),
            "version": self.metadata.get("version", "Unknown"),
            "record_count": self.metadata.get("record", "Unknown"),
            "description": self.metadata.get("description", "").strip(),
            "title": self.metadata.get("title", self.name),
            "encoding": self.metadata.get("encoding", "UTF-8"),
            "format": self.metadata.get("format", "Unknown"),
            "creation_date": self.metadata.get("creationdate", "Unknown"),
        }
    
    async def get_keys(self) -> Set[str]:
        """Get all keys (words) in this dictionary, with caching."""
        if self._keys_cache is None:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._keys_cache = await loop.run_in_executor(
                None, 
                lambda: set(get_keys(str(self.path)))
            )
        return self._keys_cache
    
    async def lookup(self, word: str) -> Optional[str]:
        """Look up a word in this dictionary."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._sync_lookup(word)
            )
            return result
        except Exception as e:
            logging.getLogger(__name__).error(f"Error looking up '{word}' in {self.name}: {e}")
            return None
    
    def _sync_lookup(self, word: str) -> Optional[str]:
        """Synchronous lookup helper using mdict_utils.reader.query."""
        try:
            # Use the official query method from mdict_utils
            content = query(str(self.path), word)
            if content:
                return self._clean_content(content)
            return None
        except Exception as e:
            # If exact query fails, try fallback with manual search
            logging.getLogger(__name__).debug(f"Query failed for '{word}', trying fallback: {e}")
            return self._fallback_lookup(word)
    
    def _fallback_lookup(self, word: str) -> Optional[str]:
        """Fallback lookup method for partial matching."""
        try:
            # Get all keys and do case-insensitive matching
            all_keys = get_keys(str(self.path))
            word_lower = word.lower()
            
            # Try to find a key that starts with the word (case-insensitive)
            for key in all_keys:
                if key.lower().startswith(word_lower):
                    content = query(str(self.path), key)
                    if content:
                        return self._clean_content(content)
            
            return None
        except Exception as e:
            logging.getLogger(__name__).error(f"Fallback lookup failed for '{word}': {e}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """Clean and format dictionary content."""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove CSS links and head tags for cleaner display
        content = re.sub(r'<head>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<link[^>]*>', '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    async def search(self, pattern: str, limit: int = 10) -> List[str]:
        """Search for words matching a pattern."""
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self._sync_search(pattern, limit)
            )
            return results
        except Exception as e:
            logging.getLogger(__name__).error(f"Error searching '{pattern}' in {self.name}: {e}")
            return []
    
    def _sync_search(self, pattern: str, limit: int) -> List[str]:
        """Synchronous search helper using mdict_utils.reader.get_keys."""
        try:
            # Get all keys using the official API
            all_keys = get_keys(str(self.path))
            pattern_lower = pattern.lower()
            matches = []
            
            # Search through dictionary keys
            for key in all_keys:
                if len(matches) >= limit:
                    break
                
                key_lower = key.lower()
                if pattern_lower in key_lower:
                    matches.append(key)
            
            return sorted(matches)
        except Exception as e:
            logging.getLogger(__name__).error(f"Search failed for '{pattern}': {e}")
            return []


class DictionaryManager:
    """Manages multiple MDict dictionaries."""
    
    def __init__(self):
        self.dictionaries: Dict[str, DictionaryInfo] = {}
        self.logger = logging.getLogger(__name__)
    
    async def load_dictionary(self, path: Path) -> None:
        """Load a dictionary from an MDX file."""
        if not path.exists():
            raise FileNotFoundError(f"Dictionary file not found: {path}")
        
        if not path.suffix.lower() == '.mdx':
            raise ValueError(f"File must be an MDX file: {path}")
        
        try:
            # Load metadata in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            metadata = await loop.run_in_executor(
                None,
                lambda: self._load_metadata_sync(path)
            )
            
            # Create dictionary info
            name = path.stem
            dict_info = DictionaryInfo(name, path, metadata)
            
            self.dictionaries[name] = dict_info
            self.logger.info(f"Successfully loaded dictionary: {name} ({metadata.get('Record', 'Unknown')} entries)")
            
        except Exception as e:
            self.logger.error(f"Failed to load dictionary {path}: {e}")
            raise
    
    def _load_metadata_sync(self, path: Path) -> Dict[str, Any]:
        """Synchronously load dictionary metadata using mdict_utils.reader.meta."""
        try:
            # Use the official meta method from mdict_utils
            metadata = meta(str(path))
            return metadata
        except Exception as e:
            self.logger.warning(f"Failed to load metadata for {path}: {e}")
            # Return basic metadata if official method fails
            return {
                "title": path.stem,
                "description": f"MDict dictionary: {path.name}",
                "record": "Unknown",
                "version": "Unknown",
                "encoding": "UTF-8",
                "format": "MDict",
                "creationdate": "Unknown"
            }
    
    async def lookup_word(self, word: str, dictionary_name: Optional[str] = None) -> Optional[str]:
        """Look up a word in dictionaries."""
        if not word.strip():
            return None
        
        if dictionary_name:
            # Look up in specific dictionary
            if dictionary_name in self.dictionaries:
                return await self.dictionaries[dictionary_name].lookup(word)
            else:
                raise ValueError(f"Dictionary '{dictionary_name}' not found")
        else:
            # Look up in all dictionaries, return first match
            for dict_info in self.dictionaries.values():
                result = await dict_info.lookup(word)
                if result:
                    return result
            return None
    
    async def search_words(self, pattern: str, limit: int = 10, dictionary_name: Optional[str] = None) -> List[str]:
        """Search for words matching a pattern in dictionaries."""
        if not pattern.strip():
            return []
        
        if dictionary_name:
            # Search in specific dictionary
            if dictionary_name in self.dictionaries:
                return await self.dictionaries[dictionary_name].search(pattern, limit)
            else:
                raise ValueError(f"Dictionary '{dictionary_name}' not found")
        else:
            # Search in all dictionaries
            all_matches = set()
            
            for dict_info in self.dictionaries.values():
                matches = await dict_info.search(pattern, limit)
                all_matches.update(matches)
                
                # Stop if we have enough matches
                if len(all_matches) >= limit:
                    break
            
            # Return sorted, limited results
            return sorted(list(all_matches))[:limit]
    
    async def list_dictionaries(self) -> List[Dict[str, Any]]:
        """List all loaded dictionaries with their metadata."""
        return [dict_info.get_metadata() for dict_info in self.dictionaries.values()]
    
    def get_dictionary_count(self) -> int:
        """Get the number of loaded dictionaries."""
        return len(self.dictionaries)
    
    def get_dictionary_names(self) -> List[str]:
        """Get list of loaded dictionary names."""
        return list(self.dictionaries.keys()) 