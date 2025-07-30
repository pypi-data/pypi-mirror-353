# Tools


<table>
<tr>
<td> Tool </td> <td> Request </td> <td> Response </td>
</tr>
<tr>
<td> lookup_word </td>
<td>

```json
{
  "word": "science",
  "dictionary": "optional_specific_dictionary_name"
}
```

</td>
<td>

```json
{
  "word": "science",
  "found": true,
  "dictionary": null,
  "definition": "<HTML definition content>",
  "success": true
}
```

</td>
</tr>
<tr>
<td> search_words </td>
<td>

```json
{
  "pattern": "sci",
  "limit": 10,
  "dictionary": "optional_specific_dictionary_name"
}
```

</td>
<td>

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

</td>
</tr>
<tr>
<td> find_similar_words </td>
<td>

```json
{
  "word": "science",
  "dictionary": "optional_specific_dictionary_name",
  "limit": 10,
  "max_distance": 2
}
```

</td>
<td>

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

</td>
</tr>
<tr>
<td> list_dictionaries </td>
<td>

None

</td>
<td>

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

</td>
</tr>
<tr>
<td> scan_dictionaries </td>
<td>

None

</td>
<td>

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

</td>
</tr>
<tr>
<td> get_dictionary_metadata </td>
<td>

```json
{
  "dictionary": "dictionary_name"
}
```

</td>
<td>

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

</td>
</tr>
<tr>
<td> get_dictionary_keys </td>
<td>

```json
{
  "dictionary": "dictionary_name",
  "limit": 100,
  "prefix": "optional_prefix"
}
```

</td>
<td>

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

</td>
</tr>
</table>