# 📂 Code Explorer - Folder Structure

## 🌳 Complete Directory Tree

```
CodeDevour/
│
├── 📁 server/                          # Backend application
│   │
│   ├── 📁 visualizer/                  # 🆕 CODE EXPLORER MODULE
│   │   ├── 📄 __init__.py              # Module initialization & exports
│   │   ├── 📄 parser.py                # Python AST parser
│   │   ├── 📄 dependency_analyzer.py   # Dependency graph builder
│   │   ├── 📄 cache_manager.py         # File-based caching system
│   │   └── 📁 cache/                   # Cache storage directory
│   │       ├── 📄 .gitignore           # Exclude cache from git
│   │       └── 📁 project_<hash>/      # Per-project cache
│   │           ├── 📄 files.json       # Parsed files data
│   │           ├── 📄 dependencies.json # Dependency graph
│   │           └── 📄 metadata.json    # Cache metadata
│   │
│   ├── 📁 routes/                      # API endpoints
│   │   ├── 📄 __init__.py              # Blueprint registration
│   │   ├── 📄 visualizer.py            # 🆕 Visualizer API endpoints
│   │   ├── 📄 text.py                  # Text extraction routes
│   │   ├── 📄 names.py                 # File tree routes
│   │   ├── 📄 lists.py                 # Exclusion list routes
│   │   └── 📄 config_routes.py         # Config management routes
│   │
│   ├── 📁 services/                    # Business logic
│   │   ├── 📄 metrics.py               # Token counting, stats
│   │   ├── 📄 cleaners.py              # File content cleaning
│   │   └── 📄 gitignore_sync.py        # .gitignore syncing
│   │
│   ├── 📁 extractors/                  # Core extraction logic
│   │   ├── 📄 TextEXtractor.py         # Text bundler
│   │   └── 📄 NamesExtractor.py        # File tree generator
│   │
│   ├── 📁 templates/                   # HTML templates
│   │   ├── 📄 Extractor.html           # Main UI
│   │   └── 📄 Tree.html                # File tree template
│   │
│   ├── 📄 app.py                       # Flask application entry
│   └── 📄 config.py                    # Configuration loader
│
├── 📁 tests/                           # Test suite
│   │
│   └── 📁 visualizer/                  # 🆕 Visualizer tests
│       ├── 📄 __init__.py
│       ├── 📄 test_parser.py           # CodeParser unit tests
│       └── 📄 test_dependency_analyzer.py  # DependencyAnalyzer tests
│
├── 📁 static/                          # Frontend assets
│   ├── 📄 site.webmanifest
│   └── (CSS, JS to be added in Week 2)
│
├── 📁 Downloads/                       # Output directory
│   └── 📁 CodeDevourBundle/
│
├── 📄 config.json                      # App configuration
├── 📄 exclude_me.txt                   # Exclusion list
├── 📄 requirements.txt                 # Python dependencies
├── 📄 run_app.py                       # App launcher
├── 📄 README.md                        # Main documentation
│
├── 📄 FEATURE_CODE_EXPLORER.md         # Feature specification
├── 📄 BACKEND_IMPLEMENTATION.md        # Backend docs
├── 📄 WEEK1_COMPLETE.md               # Week 1 summary
├── 📄 FOLDER_STRUCTURE.md             # This file
└── 📄 test_visualizer_backend.py      # Integration test script
```

---

## 📦 Module Details

### 🆕 server/visualizer/ - Code Explorer Core

```
visualizer/
├── __init__.py              # Exports: CodeParser, DependencyAnalyzer, CacheManager
├── parser.py                # 243 lines - Python AST parsing
├── dependency_analyzer.py   # 357 lines - Graph building & analysis
├── cache_manager.py         # 356 lines - Caching system
└── cache/                   # Auto-managed cache directory
    ├── .gitignore          # Ignores all cache files
    └── project_abc123def/  # Example cached project
        ├── files.json
        ├── dependencies.json
        └── metadata.json
```

**Purpose:**
- Parse Python source code
- Build dependency graphs
- Cache results for performance

---

### 🔌 server/routes/visualizer.py - API Endpoints

```python
Blueprint: 'visualizer'
Prefix: /api/visualizer/

Endpoints:
├── POST   /scan               # Scan project, build graphs
├── GET    /graph              # Get dependency graph data
├── GET    /file/<path>        # Get file details
├── GET    /stats              # Get statistics
└── POST   /cache/clear        # Clear cache
```

**Integration:**
- Registered in `server/routes/__init__.py`
- Uses visualizer module components
- Returns JSON for frontend consumption

---

### 🧪 tests/visualizer/ - Test Suite

```
tests/visualizer/
├── __init__.py
├── test_parser.py                  # 10 test cases
│   ├── test_parse_simple_function
│   ├── test_parse_function_with_parameters
│   ├── test_parse_class_with_methods
│   ├── test_parse_imports
│   ├── test_parse_function_calls
│   ├── test_parse_async_function
│   └── ...
│
└── test_dependency_analyzer.py    # 4 test cases
    ├── test_simple_file_graph
    ├── test_function_graph
    ├── test_centrality_calculation
    └── test_get_file_dependencies
```

**Run Tests:**
```bash
# Individual module tests
python server/visualizer/parser.py
python server/visualizer/cache_manager.py

# Integration test
python test_visualizer_backend.py
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
│                     (server/app.py)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ├── Blueprints registered
                      │
        ┌─────────────┼─────────────┬─────────────┬───────────┐
        │             │             │             │           │
        ▼             ▼             ▼             ▼           ▼
   text_bp      names_bp      lists_bp    config_bp   visualizer_bp
        │             │             │             │           │
        │             │             │             │           │
        └─────────────┴─────────────┴─────────────┴───────────┘
                                                              │
                                                              ▼
                                            ┌─────────────────────────────┐
                                            │  Visualizer Routes          │
                                            │  (routes/visualizer.py)     │
                                            └──────────┬──────────────────┘
                                                       │
                    ┌──────────────────────────────────┼──────────────────┐
                    │                                  │                  │
                    ▼                                  ▼                  ▼
          ┌─────────────────┐              ┌──────────────────┐  ┌───────────────┐
          │   CodeParser    │              │ DependencyAnalyzer│  │ CacheManager  │
          │  (parser.py)    │              │(dependency_*.py)  │  │(cache_*.py)   │
          └────────┬────────┘              └─────────┬────────┘  └───────┬───────┘
                   │                                 │                    │
                   │ parses                          │ builds             │ caches
                   │                                 │                    │
                   ▼                                 ▼                    ▼
            Python Files                      Dependency Graph        JSON Files
            (.py source)                     (nodes + edges)         (cache/*.json)
```

---

## 🗂️ File Responsibilities

### Core Components:

| File | Responsibility | Key Functions |
|:-----|:---------------|:-------------|
| `parser.py` | Parse Python AST | `parse_file()`, `_extract_functions()`, `_extract_imports()` |
| `dependency_analyzer.py` | Build graphs | `build_file_graph()`, `build_function_graph()`, `detect_circular_dependencies()` |
| `cache_manager.py` | Cache management | `save_parsed_files()`, `load_parsed_files()`, `is_cache_valid()` |
| `routes/visualizer.py` | REST API | `/scan`, `/graph`, `/file/<path>`, `/stats` |

### Supporting Files:

| File | Purpose |
|:-----|:--------|
| `__init__.py` | Module exports and initialization |
| `test_parser.py` | Unit tests for CodeParser |
| `test_dependency_analyzer.py` | Unit tests for DependencyAnalyzer |
| `test_visualizer_backend.py` | Integration test suite |

---

## 📋 File Sizes

```
server/visualizer/
├── parser.py                    ~9 KB  (243 lines)
├── dependency_analyzer.py       ~11 KB (357 lines)
├── cache_manager.py             ~11 KB (356 lines)
└── __init__.py                  ~1 KB

server/routes/
└── visualizer.py                ~7 KB  (232 lines)

tests/visualizer/
├── test_parser.py               ~5 KB  (184 lines)
└── test_dependency_analyzer.py  ~4 KB  (137 lines)

Total: ~48 KB production code
       ~9 KB test code
```

---

## 🎯 Clean Separation

### ✅ Modular Design:

**No Mixing:**
- ❌ Visualizer code NOT in existing routes
- ❌ Parser code NOT scattered across files
- ❌ Cache NOT in random directories

**Clear Boundaries:**
- ✅ Visualizer has own folder: `server/visualizer/`
- ✅ API has own route file: `routes/visualizer.py`
- ✅ Tests have own folder: `tests/visualizer/`
- ✅ Cache has dedicated directory: `visualizer/cache/`

**Dependencies:**
```python
# Visualizer is self-contained
from server.visualizer import CodeParser, DependencyAnalyzer, CacheManager

# Minimal external dependencies
- ast (built-in)
- os (built-in)
- json (built-in)
- typing (built-in)
```

---

## 🔐 Security & Best Practices

### Cache Directory:
```
server/visualizer/cache/
└── .gitignore           # Auto-generated
    *                    # Ignore all files
    !.gitignore          # Except this file
```

**Why:**
- Cache contains project-specific data
- Can be large (MBs for big projects)
- Should not be committed to git
- Auto-regenerated when needed

### Module Initialization:
```python
# server/visualizer/__init__.py
from .parser import CodeParser
from .dependency_analyzer import DependencyAnalyzer
from .cache_manager import CacheManager

__all__ = ['CodeParser', 'DependencyAnalyzer', 'CacheManager']
```

**Benefits:**
- Clean public API
- Hide internal implementation
- Easy imports: `from server.visualizer import CodeParser`

---

## 📖 Usage Examples

### Importing Components:

```python
# Option 1: Import from package
from server.visualizer import CodeParser, DependencyAnalyzer, CacheManager

# Option 2: Import specific module
from server.visualizer.parser import CodeParser
from server.visualizer.dependency_analyzer import DependencyAnalyzer
from server.visualizer.cache_manager import CacheManager

# Option 3: Import entire package
import server.visualizer as viz
parser = viz.CodeParser()
```

### File Paths:

```python
import os

# Project structure
project_root = 'C:/Users/Andri/Project/CodeDevour'

# Parser
parser_path = os.path.join(project_root, 'server', 'visualizer', 'parser.py')

# API Routes
routes_path = os.path.join(project_root, 'server', 'routes', 'visualizer.py')

# Cache
cache_dir = os.path.join(project_root, 'server', 'visualizer', 'cache')

# Tests
test_path = os.path.join(project_root, 'tests', 'visualizer', 'test_parser.py')
```

---

## 🚀 Next Steps (Week 2)

### Frontend Files to Create:

```
static/
├── js/
│   └── visualizer/              # 🔜 To be created
│       ├── BubbleGraph.js       # D3.js graph
│       ├── DetailsSidebar.js    # File details panel
│       └── FilterPanel.js       # Search & filters
│
└── css/
    └── visualizer.css           # 🔜 Visualization styles

templates/
└── CodeExplorer.html            # 🔜 New tab UI
```

---

**Document Version:** 1.0  
**Last Updated:** October 26, 2025  
**Status:** 🟢 Week 1 Complete - Structure Documented
