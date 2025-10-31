# 📂 Project Folder Structure

This document provides a detailed overview of the CodeDevour project structure, highlighting the roles of key directories and files.

## 🌳 Directory Tree

```
CodeDevour/
│
├── 📁 server/                          # Backend application (Flask)
│   ├── 📁 visualizer/                  # Core Code Explorer module
│   │   ├── 📄 parser.py                # Multi-language code parser
│   │   ├── 📄 dependency_analyzer.py   # Dependency graph builder
│   │   └── 📄 cache_manager.py         # Caching for visualization data
│   │
│   ├── 📁 routes/                      # API endpoints
│   │   ├── 📄 visualizer.py            # Endpoints for the Code Explorer
│   │   ├── 📄 text.py                  # Endpoints for the text bundler
│   │   └── ...                         # Other routes
│   │
│   ├── 📁 services/                    # Business logic
│   ├── 📁 extractors/                  # Core extraction logic
│   ├── 📁 templates/                   # HTML templates
│   │   ├── 📄 CodeExplorer.html        # Main UI for the visualizer
│   │   └── ...
│   │
│   ├── 📄 app.py                       # Flask application entry point
│   └── 📄 config.py                    # Configuration loader
│
├── 📁 static/                          # Frontend assets
│   ├── 📁 js/
│   │   └── 📁 visualizer/
│   │       ├── 📄 BubbleGraph.js       # D3.js graph logic
│   │       ├── 📄 DetailsSidebar.js    # File details panel logic
│   │       └── 📄 FilterPanel.js       # Search and filter logic
│   │
│   └── 📁 css/
│       └── 📄 visualizer.css           # Styles for the visualizer
│
├── 📄 requirements.txt                 # Python dependencies
├── 📄 README.md                        # Main documentation
└── ...                                # Other configuration files
```

---

## 📦 Module Details

### `server/visualizer/` - Code Explorer Core

This directory contains the core logic for parsing code and building the dependency graph.

- **`parser.py`**: A multi-language parser that uses AST for Python and JavaScript/TypeScript, and regex for other languages. It extracts functions, classes, imports, and `require` statements.
- **`dependency_analyzer.py`**: Builds the dependency graph by resolving imports and `require` statements. It now dynamically handles path aliases from `tsconfig.json` or `jsconfig.json`.
- **`cache_manager.py`**: Caches parsed data and dependency graphs to improve performance on subsequent scans.

### `server/routes/visualizer.py` - API Endpoints

This file defines the API endpoints that power the Code Explorer frontend. It handles requests for scanning projects, retrieving graph data, and fetching file details.

### `static/js/visualizer/` - Frontend Logic

This directory contains the JavaScript files that render the interactive visualization.

- **`BubbleGraph.js`**: Manages the D3.js force-directed graph.
- **`DetailsSidebar.js`**: Controls the panel that displays details for selected files.
- **`FilterPanel.js`**: Handles the search and filtering functionality.

---

## 🔄 Data Flow

1.  **Scan Request**: The frontend sends a request to the `/api/visualizer/scan` endpoint.
2.  **Parsing**: The `CodeParser` processes each file, extracting its structure.
3.  **Dependency Analysis**: The `DependencyAnalyzer` resolves imports and builds the dependency graph.
4.  **Caching**: The results are cached by the `CacheManager`.
5.  **Graph Data**: The frontend fetches the graph data from `/api/visualizer/graph` and renders it using D3.js.
6.  **File Details**: When a node is clicked, the frontend requests its details from `/api/visualizer/file/<path>` and displays them in the sidebar.

---

This modular structure ensures a clean separation of concerns and makes the application easier to maintain and extend.
