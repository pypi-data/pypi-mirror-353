# Storage Backends

Storage backends in doteval handle the persistence of evaluation sessions, results, and metadata. They provide a consistent interface for saving and loading evaluation data while supporting different storage mechanisms.

## Overview

Storage backends implement the `Storage` abstract base class and provide session persistence.

## Built-in Storage Backends

### JSON Storage (Default)

The JSON storage backend stores each session as a separate JSON file in a directory.

```python
from doteval.storage import JSONStorage

# Create JSON storage in default location
storage = JSONStorage("evals")

# Custom path
storage = JSONStorage("/path/to/my/evaluations")
```

**Directory Structure:**
```
evals/
├── gsm8k_baseline.json      # Session data
├── gsm8k_baseline.lock      # Lock file (if running)
├── sentiment_eval.json
└── math_reasoning.json
```

**Features:**
- Human-readable JSON format
- File-based locking
- Automatic directory creation
- Cross-platform compatibility

**Usage via URL:**
```bash
# Default JSON storage
doteval list --storage "json://evals"

# Custom path
doteval list --storage "json:///absolute/path/to/storage"

# Relative path
doteval list --storage "json://relative/path"
```

## Error Handling

The storage system provides helpful error messages for common configuration issues:

### Invalid Storage Paths

```bash
# Missing backend specification
$ doteval list --storage "invalid_path"
Error: Invalid storage path 'invalid_path'. Storage paths must be in the format 'backend://path'. Currently supported: json://path

# Unsupported backend
$ doteval list --storage "postgres://localhost"
Error: Unsupported storage backend 'postgres'. Currently supported backends: json. Use 'json://path' instead of 'postgres://localhost'
```

### Permission Issues

```bash
# No write permissions
$ doteval list --storage "json:///root/restricted"
Error: Permission denied: Cannot write to '/root/restricted'
```

### Storage Recovery

If storage files become corrupted or inaccessible:

```python
from doteval.storage import JSONStorage

storage = JSONStorage("evals")

# Check if session exists
if storage.exists("my_session"):
    try:
        session = storage.load("my_session")
    except Exception as e:
        print(f"Session corrupted: {e}")
        # Session file may need manual recovery
```
