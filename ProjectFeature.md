# CodeDevour - Project Feature Documentation

## Overview

**CodeDevour** is a powerful web-based tool for exploring project structure, bundling code files, and managing file exclusions through an intuitive interface. It transforms any codebase into a single, well-organized document perfect for documentation, code review, AI analysis, or academic purposes.

---

## Table of Contents

1. [Core Features](#core-features)
2. [Dashboard Interface](#dashboard-interface)
3. [Code Explorer](#code-explorer)
4. [File Management Features](#file-management-features)
5. [Backend Architecture](#backend-architecture)
6. [Visualization Engine](#visualization-engine)
7. [API Endpoints](#api-endpoints)
8. [Configuration](#configuration)
9. [Technology Stack](#technology-stack)

---

## Core Features

### 1. Multi-Language Code Visualizer

The code visualizer supports **13+ programming languages** with smart parsing capabilities:

#### Supported Languages
| Language | Parser Type | Extensions |
|----------|-------------|------------|
| Python | AST (native) | `.py` |
| JavaScript | Esprima + Regex | `.js`, `.jsx` |
| TypeScript | Esprima + Regex | `.ts`, `.tsx` |
| Java | Regex | `.java` |
| C/C++ | Regex | `.c`, `.cpp`, `.h`, `.hpp` |
| Go | Regex | `.go` |
| Rust | Regex | `.rs` |
| PHP | Regex | `.php` |
| Ruby | Regex | `.rb` |
| C# | Regex | `.cs` |
| Swift | Regex | `.swift` |
| Kotlin | Regex | `.kt`, `.kts` |
| Vue | Regex | `.vue` |

#### Parsing Capabilities
- **Functions/Methods**: Name, line numbers, parameters, decorators
- **Classes**: Base classes, methods, access modifiers
- **Imports**: Module names, imported items, line numbers
- **Function Calls**: Called functions within functions/methods

#### Smart Features
- Dynamic alias resolution from `tsconfig.json` or `jsconfig.json`
- Technology stack detection (React, Vue, Next.js, Express, etc.)
- Centrality metrics for identifying important files
- Circular dependency detection

### 2. Interactive Project Explorer

#### Visual File Tree
- Lazy-loading folder sizes for fast performance
- Collapsible folders with smooth animations
- Drag-and-drop filtering between lists
- Color-coded file types

#### Drag-and-Drop Filtering
- Drag files/folders from tree to **Exclude Me** tab
- Drag files/folders to **Just Me** tab for inclusion filtering
- Real-time list updates

### 3. Smart Text Bundler

#### File Extraction
- Automatic file merging into single text file
- Supports **30+ file extensions**
- BA/WA delimiters for file separation (BA = Border Above, WA = Border Below)
- Formatted and raw output modes

#### Output Format
```
BA
'/path/to/file.py'
[file content]
WA
```

#### Metrics & Analysis
- Real-time token counting (tiktoken-based)
- Word count tracking
- Line count statistics
- Progress tracking for large projects

---

## Dashboard Interface

### Main Dashboard (`/`)

The main dashboard provides access to all core features through a tabbed interface.

#### Navigation Chips
```
[NamesExtractor] [TextExtractor] [Exclude Me] [Just Me] [Activity Log] [Code Explorer]
```

#### 1. NamesExtractor Panel

**Purpose**: Generate a list of files and folders in the project.

**Features**:
- ✅ Include Files toggle
- ✅ Include Size toggle (shows file/folder sizes)
- Collapsible folder tree
- Drag-and-drop to exclusion lists
- JSON and text output formats

**Endpoint**: `/run_nameextractor_json`

#### 2. TextExtractor Panel

**Purpose**: Bundle all code files into a single output file.

**Features**:
- Custom output directory selection
- Custom output filename
- Remove blank lines option
- **Async extraction mode** (with progress bar)
- **Auto-visualize** option (opens Code Explorer after extraction)
- 128KB chunk streaming for large files
- Progress tracking:
  - Current file being processed
  - Files processed count
  - ETA calculation
  - Duration tracking

**Endpoints**:
- `/run_textextractor` - Synchronous
- `/run_textextractor_async` - Asynchronous
- `/tasks/start_extraction` - Task-based async

#### 3. Exclude Me Panel

**Purpose**: Manage blacklist of files/folders to exclude from extraction.

**Features**:
- Edit exclusion patterns directly
- Patterns support:
  - Filename: `page.html`
  - Relative path: `src/pages/page.html`
  - Substring match: `/node_modules/`, `.log`
- Auto-sync with `.gitignore` when path is set
- Drag-and-drop from file tree

**File**: `lists/exclude_me.txt`

#### 4. Just Me Panel

**Purpose**: Manage whitelist/inclusion filter for selective extraction.

**Features**:
- Define specific files/folders to include
- Pattern matching:
  - Filename: `app.py`
  - Folder path: `src/components/`
  - Nested file detection (scans subdirectories)
- Empty pattern = process all files (subject to exclusions)

**File**: `lists/just_me.txt`

#### 5. Activity Log Panel

**Purpose**: Real-time status and logging.

**Features**:
- Timestamped log entries
- Color-coded messages (info, success, error)
- Auto-scroll to latest entries

---

## Code Explorer

### Access
Navigate to: `/visualizer`

### Features

#### 1. Interactive Bubble Graph

**Technology**: D3.js Force-Directed Graph

**Visual Elements**:
- **Bubbles**: Represent files
- **Lines**: Represent import dependencies
- **Bubble Size**: Indicates importance (centrality score)
- **Colors**: Represent programming language/framework

**Language/Framework Colors**:
| Framework | Color |
|-----------|-------|
| Python | `#3572A5` (Blue) |
| JavaScript | `#F1E05A` (Yellow) |
| TypeScript | `#2B7489` (Teal) |
| React | `#61DAFB` (Light Blue) |
| Next.js | `#000000` (Black) |
| Vue | `#4FC08D` (Green) |
| Node.js | `#68A063` (Green) |
| Angular | `#DD0031` (Red) |
| Default | `#DC143C` (Crimson) |

**Interactions**:
- **Click**: Select file, highlight dependencies, show details
- **Drag**: Reposition bubbles
- **Scroll**: Zoom in/out
- **Pan**: Click and drag background

#### 2. File Tree Panel

**Features**:
- Hierarchical folder structure
- Collapsible folders
- Click to focus on file in graph
- Shows availability status (parsed vs. filtered)
- Auto-sync with graph data

#### 3. Filter Panel

**Features**:
- Language filter (all or specific language)
- Size-based filtering
- Search functionality
- Real-time graph updates

#### 4. Details Sidebar

**Displays**:
- File metadata (path, size, lines)
- Programming language
- Functions (with line numbers)
- Classes (with methods)
- Import statements
- Dependencies (imports vs. imported by)

#### 5. Graph Controls

| Control | Function |
|---------|----------|
| ↻ | Reset view to center |
| 💾 | Export graph as SVG |
| ⛶ | Toggle fullscreen |
| [Analyze Project] | Scan and visualize project |
| [Update Analysis] | Refresh with latest changes |
| [Clear Data] | Clear cached data |

---

## File Management Features

### 1. Async Task Processing

**Purpose**: Handle long-running extraction tasks without browser timeouts.

**Features**:
- Background thread execution
- Real-time progress polling
- Task cancellation support
- Automatic cleanup of old tasks (24-hour TTL)
- Task statistics tracking

**States**:
- `pending` - Task created, not started
- `running` - Currently processing
- `completed` - Successfully finished
- `failed` - Error occurred
- `cancelled` - User cancelled

### 2. Gitignore Sync

**Purpose**: Automatically import `.gitignore` patterns into exclusion list.

**Behavior**:
- Triggers when project path is set
- Merges patterns with existing exclusions
- Adds marker comment for synced patterns
- Updates `lists/exclude_me.txt`

### 3. Memory Management

**Purpose**: Prevent memory issues with large projects.

**Features**:
- Memory usage monitoring (psutil)
- Garbage collection triggers
- 80% memory threshold warning
- Configurable max file size (default 10MB)

### 4. Output Cleaning

**Purpose**: Post-processing of extracted content.

**Features**:
- Blank line removal
- In-place file modification
- Statistics on removed lines

---

## Backend Architecture

### Application Structure

```
server/
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── routes/
│   ├── config_routes.py  # Project path, folder picker
│   ├── text.py           # Text extraction endpoints
│   ├── names.py          # Names extraction endpoints
│   ├── lists.py          # Exclude/just_me management
│   ├── task_routes.py    # Async task management
│   └── visualizer.py     # Code visualization API
├── extractors/
│   ├── NamesExtractor.py      # File listing
│   ├── TextEXtractor.py       # Legacy bundler
│   └── EnhancedTextExtractor.py # Advanced bundler
├── services/
│   ├── task_manager.py    # Async task handling
│   ├── gitignore_sync.py  # .gitignore integration
│   ├── cleaners.py        # Text cleaning utilities
│   ├── metrics.py         # Statistics calculation
│   └── smart_filter.py    # Filtering logic
└── visualizer/
    ├── parser.py              # Multi-language code parser
    ├── dependency_analyzer.py # Dependency graph builder
    └── cache_manager.py       # Performance caching
```

### Flask Blueprints

| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| `config_bp` | `/` | Configuration management |
| `text_bp` | `/run_textextractor` | Text bundling |
| `names_bp` | `/run_nameextractor` | File listing |
| `lists_bp` | `/manage_*` | Exclusion/inclusion lists |
| `task_bp` | `/tasks/*` | Async task management |
| `visualizer_bp` | `/api/visualizer/*` | Code visualization |

---

## Visualization Engine

### Code Parser (`parser.py`)

**Class**: `CodeParser`

#### Methods
| Method | Returns | Description |
|--------|---------|-------------|
| `parse_file(filepath)` | `Dict\|None` | Parse single file |
| `is_supported(filepath)` | `bool` | Check extension support |
| `_parse_python_file(filepath)` | `Dict` | AST-based Python parsing |
| `_parse_js_ts_file(filepath)` | `Dict` | Esprima + regex JS/TS parsing |
| `_parse_java_file(filepath)` | `Dict` | Regex-based Java parsing |
| `_parse_c_cpp_file(filepath)` | `Dict` | Regex-based C/C++ parsing |
| `_parse_go_file(filepath)` | `Dict` | Regex-based Go parsing |
| `_parse_rust_file(filepath)` | `Dict` | Regex-based Rust parsing |
| `_parse_php_file(filepath)` | `Dict` | Regex-based PHP parsing |
| `_parse_ruby_file(filepath)` | `Dict` | Regex-based Ruby parsing |
| `_parse_csharp_file(filepath)` | `Dict` | Regex-based C# parsing |
| `_parse_swift_file(filepath)` | `Dict` | Regex-based Swift parsing |
| `_parse_kotlin_file(filepath)` | `Dict` | Regex-based Kotlin parsing |

#### Output Structure
```python
{
    'filepath': str,
    'language': str,
    'size': int,
    'lines': int,
    'functions': [
        {
            'name': str,
            'line_start': int,
            'line_end': int,
            'parameters': [str],
            'calls': [str],
            'decorators': [str],
            'is_async': bool
        }
    ],
    'classes': [
        {
            'name': str,
            'line_start': int,
            'line_end': int,
            'bases': [str],
            'methods': [...],
            'decorators': [str]
        }
    ],
    'imports': [
        {
            'module': str,
            'items': [str],
            'line': int
        }
    ]
}
```

### Dependency Analyzer (`dependency_analyzer.py`)

**Class**: `DependencyAnalyzer`

#### Methods
| Method | Returns | Description |
|--------|---------|-------------|
| `build_file_graph()` | `Dict` | File-level dependency graph |
| `build_function_graph()` | `Dict` | Function call graph |
| `detect_circular_dependencies()` | `List[List[str]]` | Find circular imports |
| `find_dead_code()` | `Dict` | Identify unused code |
| `get_file_dependencies(filepath)` | `Dict` | Get file's dependencies |

#### Graph Output Structure
```python
{
    'nodes': [
        {
            'id': str,          # Relative file path
            'type': 'file',
            'size': int,
            'lines': int,
            'language': str,
            'functions_count': int,
            'classes_count': int,
            'centrality': float,  # 0-1 importance score
            'in_degree': int,     # Number of imports
            'out_degree': int     # Number of importers
        }
    ],
    'edges': [
        {
            'source': str,
            'target': str,
            'type': 'import',
            'module': str,
            'items': [str]
        }
    ]
}
```

### Cache Manager

**Purpose**: Cache parsed results for performance.

**Cached Data**:
- Parsed files (per-file metadata)
- Dependency graphs
- Scan metadata (timestamp, counts)

**Cache Invalidation**:
- Automatic when filter patterns change
- Manual clear via API
- Project-specific cache isolation

---

## API Endpoints

### Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/set_path` | Set project path |
| GET | `/pick_folder` | Open folder picker dialog |
| GET | `/pick_output_folder` | Open output folder picker |
| GET | `/config_summary` | Get current configuration |

### File Extraction

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/run_textextractor` | Synchronous text extraction |
| POST | `/run_textextractor_async` | Async text extraction |
| GET | `/output_metrics` | Get output file statistics |
| GET | `/open_output_folder` | Open output folder in explorer |

### File Listing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/run_nameextractor` | Legacy extraction (text) |
| POST | `/run_nameextractor_json` | JSON extraction |
| GET | `/size` | Get file/folder size |

### List Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/manage_exclude_file` | Manage exclusion list |
| GET/POST | `/manage_just_me` | Manage inclusion list |

### Task Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks/start_extraction` | Start async extraction task |
| GET | `/tasks/task_status/<id>` | Get task status |
| GET | `/tasks/all_tasks` | List all tasks |
| POST | `/tasks/cancel_task/<id>` | Cancel task |
| GET | `/tasks/task_result/<id>` | Get task result |
| POST | `/tasks/cleanup_tasks` | Clean up old tasks |

### Visualization

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/visualizer/scan` | Scan project & build graphs |
| GET | `/api/visualizer/graph` | Get dependency graph |
| GET | `/api/visualizer/file/<path>` | Get file details |
| GET | `/api/visualizer/stats` | Get project statistics |
| POST | `/api/visualizer/cache/clear` | Clear visualization cache |
| GET | `/api/visualizer/config` | Get filter configuration |
| GET | `/api/visualizer/file-structure` | Get hierarchical file tree |
| GET | `/visualizer` | Render Code Explorer page |

---

## Configuration

### Configuration File (`config.json`)

```json
{
    "TARGET_FOLDER": "/path/to/project",
    "OUTPUT_FILE": "/path/to/Output.txt",
    "EXCLUDE_FILE_PATH": "/path/to/exclude_me.txt",
    "JUST_ME_FILE_PATH": "/path/to/just_me.txt",
    "NAME_OUTPUT_FILE": "/path/to/OutputAllNames.txt",
    "MAX_FILE_SIZE_MB": 10,
    "FLASK_DEBUG": true
}
```

### Supported File Extensions

**Bundling (30+ extensions)**:
```
.py, .js, .ts, .tsx, .jsx, .json, .md, .txt, .html,
.css, .yml, .yaml, .toml, .ini, .cfg, .sql, .sh, .bat,
.ps1, .c, .cpp, .h, .hpp, .java, .kt, .go, .rs, .vue, .xml
```

**Visualization**:
```
.py, .js, .ts, .tsx, .jsx, .vue, .json, .html, .css
```

---

## Technology Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Python 3.8+, Flask |
| **Frontend** | HTML5, JavaScript, Tailwind CSS |
| **Visualization** | D3.js v7 |
| **JS Parsing** | Esprima |
| **Python Parsing** | AST (native), Tiktoken |
| **Task Queue** | Threading + Custom Task Manager |
| **Encoding** | UTF-8 with error handling |

---

## AI Digest Feature (`ai_digest.py`)

### Purpose
Generate AI-optimized code bundles with smart chunking.

### Features

#### Tokenizer Support
- `cl100k_base` - Default (GPT-4/4o/mini)
- `o200k_base` - Long context models (GPT-4.1/4o)

#### Smart Truncation
- Head/tail preservation
- Adaptive truncation for large files
- Token-aware chunking

#### Output Structure
```
ai-digest-[timestamp].zip
├── manifest.json           # Chunk metadata
├── INDEX.md               # File index & summaries
├── HOW_TO_USE.md          # Usage guide
├── chunks/
│   ├── chunk-0000.txt     # Overview (README, API map)
│   ├── chunk-0001.txt     # Additional files
│   └── chunk-NNNN.txt     # More files
└── files_meta.json        # File metadata
```

#### API Map Detection
- Flask routes (`@app.route`)
- FastAPI routes (`@app.get`)
- Express routes (`app.get`)
- Router patterns

---

## File Formats

### BA/WA Delimiters
```
BA                              # Border Above - Start of file
'/absolute/path/to/file.py'    # File path (quoted)
[file content]                  # Actual code
WA                              # Border Below - End of file
```

### Metadata Header
```
# lang: python
# loc: 150
# tokens: 4500
# summary: Main application entry point
```

---

## Performance Considerations

### Optimizations
1. **128KB streaming chunks** for large file output
2. **Cache invalidation** based on filter changes
3. **Lazy size calculation** for folder tree
4. **Memory monitoring** with GC triggers
5. **Background cleanup** of old tasks

### Limits
- Max file size: 10MB (configurable)
- Task timeout: 2 hours
- Task retention: 24 hours
- Max concurrent tasks: 20

---

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (limited functionality)

---

## Installation & Usage

### Quick Start
```bash
# Windows
scripts\run_app.bat

# Linux/macOS
python server/app.py
```

### Access
- Dashboard: http://127.0.0.1:5000
- Code Explorer: http://127.0.0.1:5000/visualizer

---

## Contributing

Features can be extended by:
1. Adding new parsers in `server/visualizer/parser.py`
2. Creating new extractors in `server/extractors/`
3. Adding routes in `server/routes/`
4. Extending frontend in `static/js/visualizer/`

---

*Documentation generated for CodeDevour v1.0+*
