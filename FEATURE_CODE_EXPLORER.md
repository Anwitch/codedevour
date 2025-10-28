# 🔍 Code Explorer - Interactive Codebase Visualization

## 📋 Overview

**Code Explorer** adalah fitur lanjutan CodeDevour yang memungkinkan developers untuk:
- **Visualisasi struktur codebase** dalam bentuk interactive bubble graph
- **Analisis dependencies** antar file (import/export relationships)
- **Explorasi function-level details** dengan UI yang intuitive
- **Memahami code architecture** secara visual tanpa membaca line-by-line

---

## 🎯 Problem Statement

### Current Pain Points:
1. **Sulit memahami struktur project besar** - Ribuan files, tidak tahu mana yang penting
2. **Dependency hell** - Tidak tahu file A import dari mana saja
3. **Refactoring nightmare** - Takut ubah function karena tidak tahu siapa yang pakai
4. **Onboarding lambat** - Developer baru butuh waktu lama untuk paham codebase
5. **Dead code detection** - Tidak tahu function/file mana yang tidak terpakai

### Solution:
Interactive visualization yang menunjukkan:
- File mana yang paling "central" (banyak di-import)
- Function apa saja yang ada di tiap file
- Siapa yang import function ini
- Flow dependencies secara visual

---

## 🎨 User Interface Design

### Main View: Bubble Graph

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Code Explorer                                    [Settings]│
│─────────────────────────────────────────────────────────────│
│                                                               │
│        ┌────────┐                                            │
│        │ utils/ │──────────────┐                             │
│        └────────┘              │                             │
│            │                   │                             │
│            │                   ▼                             │
│      ┌─────▼────┐         ┌────────┐                        │
│      │ config.py│────────▶│ app.py │◀────┐                  │
│      └──────────┘         └────────┘     │                  │
│                                │          │                  │
│                                │     ┌────▼─────┐            │
│                           ┌────▼────┐│ routes/ │            │
│                           │services/││         │            │
│                           └─────────┘└─────────┘            │
│                                                               │
│  Legend:                                                      │
│  ● Size = File Size    ─── = Import Relationship            │
│  ● Color = File Type   ──▶ = Export/Import Direction        │
│─────────────────────────────────────────────────────────────│
│ Selected: app.py                              [Export View] │
└─────────────────────────────────────────────────────────────┘
```

### Sidebar: File Details Panel

Ketika bubble di-klik:

```
┌─────────────────────────────────┐
│ 📄 app.py                       │
│─────────────────────────────────│
│                                 │
│ 📊 Statistics:                  │
│  • Lines: 342                   │
│  • Functions: 12                │
│  • Classes: 3                   │
│  • Imports: 8 files             │
│  • Imported by: 5 files         │
│                                 │
│ 🔧 Functions:                   │
│  ├─ create_app()               │
│  ├─ configure_routes()         │
│  ├─ handle_error()             │
│  └─ init_logging()             │
│                                 │
│ 📥 Imports from:                │
│  • config.py                   │
│  • routes/text.py              │
│  • services/metrics.py         │
│                                 │
│ 📤 Imported by:                 │
│  • run_app.py                  │
│  • tests/test_app.py           │
│                                 │
│ [View Source] [Dependency Tree] │
└─────────────────────────────────┘
```

### Function Details View

Ketika function name di-klik:

```
┌─────────────────────────────────┐
│ ⚡ create_app()                 │
│─────────────────────────────────│
│                                 │
│ 📍 Location: app.py:45          │
│ 📝 Type: Function               │
│ 🔢 Lines: 23                    │
│                                 │
│ Parameters:                     │
│  • config: dict = None          │
│                                 │
│ Returns: Flask app              │
│                                 │
│ Calls:                          │
│  ├─ configure_routes()         │
│  ├─ init_logging()             │
│  └─ Flask()                    │
│                                 │
│ Called by:                      │
│  • run_app.py:main()           │
│  • tests/test_app.py:setup()   │
│                                 │
│ [View Code] [Call Graph]        │
└─────────────────────────────────┘
```

---

## 🏗️ Technical Architecture

### 1. Backend Components

#### A. Code Parser Service (`server/visualizer/parser.py`)

```python
class CodeParser:
    """
    Parse source code files to extract:
    - Functions/methods
    - Classes
    - Import statements
    - Export statements
    """
    
    def parse_python_file(filepath):
        # Use AST (Abstract Syntax Tree)
        # Extract functions, classes, imports
        
    def parse_javascript_file(filepath):
        # Use esprima or acorn
        # Extract ES6 imports/exports
        
    def parse_typescript_file(filepath):
        # Use TypeScript compiler API
```

**Output Format:**
```json
{
  "filepath": "server/app.py",
  "language": "python",
  "size": 8432,
  "lines": 342,
  "functions": [
    {
      "name": "create_app",
      "line_start": 45,
      "line_end": 67,
      "parameters": ["config"],
      "calls": ["configure_routes", "init_logging"]
    }
  ],
  "classes": [...],
  "imports": [
    {
      "module": "flask",
      "items": ["Flask", "Blueprint"]
    },
    {
      "module": "server.config",
      "items": ["load_config"]
    }
  ]
}
```

#### B. Dependency Analyzer (`server/visualizer/dependency_analyzer.py`)

```python
class DependencyAnalyzer:
    """
    Build dependency graph:
    - Which files import which
    - Which functions call which
    - Circular dependency detection
    """
    
    def build_file_graph(parsed_files):
        # Create nodes (files) and edges (imports)
        
    def build_function_graph(parsed_files):
        # Create function-level call graph
        
    def detect_circular_dependencies():
        # Find circular import chains
        
    def find_dead_code():
        # Find unused functions/files
```

**Output Format:**
```json
{
  "nodes": [
    {
      "id": "server/app.py",
      "type": "file",
      "size": 8432,
      "language": "python",
      "centrality": 0.85
    }
  ],
  "edges": [
    {
      "source": "server/app.py",
      "target": "server/config.py",
      "type": "import",
      "items": ["load_config", "ROOT_DIR"]
    }
  ]
}
```

#### C. Visualization API (`server/routes/visualizer.py`)

```python
@visualizer_bp.route('/api/visualizer/scan', methods=['POST'])
def scan_project():
    """
    Scan project and return visualization data
    """
    
@visualizer_bp.route('/api/visualizer/file/<path:filepath>')
def get_file_details(filepath):
    """
    Get detailed info about specific file
    """
    
@visualizer_bp.route('/api/visualizer/function/<function_id>')
def get_function_details(function_id):
    """
    Get function-level details
    """
```

### 2. Frontend Components

#### A. Bubble Graph (`static/js/visualizer/BubbleGraph.js`)

```javascript
class BubbleGraph {
  constructor(containerId) {
    this.svg = d3.select(`#${containerId}`);
    this.simulation = d3.forceSimulation();
  }
  
  render(data) {
    // Create force-directed graph
    // nodes = files (bubbles)
    // links = imports (lines)
  }
  
  handleBubbleClick(fileNode) {
    // Show file details in sidebar
  }
  
  highlightDependencies(fileNode) {
    // Highlight all connected files
  }
}
```

**Features:**
- **D3.js Force Simulation** - Physics-based layout
- **Zoom & Pan** - Navigate large projects
- **Search & Filter** - Find specific files
- **Color coding** - By file type or metrics
- **Size scaling** - Based on file size or importance

#### B. Details Sidebar (`static/js/visualizer/DetailsSidebar.js`)

```javascript
class DetailsSidebar {
  showFileDetails(fileData) {
    // Render file statistics
    // List functions/classes
    // Show import/export tree
  }
  
  showFunctionDetails(functionData) {
    // Render function signature
    // Show call graph
    // Display code snippet
  }
}
```

#### C. Filter Panel (`static/js/visualizer/FilterPanel.js`)

```javascript
class FilterPanel {
  filterByLanguage(languages) {}
  filterBySize(minSize, maxSize) {}
  filterByDependencyCount(min, max) {}
  searchByName(query) {}
}
```

### 3. Data Flow

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Frontend   │────▶│  Backend API    │────▶│ Code Parser  │
│  (D3.js)     │     │  /api/visualizer│     │   (AST)      │
└──────┬───────┘     └─────────┬───────┘     └──────┬───────┘
       │                       │                     │
       │                       ▼                     │
       │              ┌─────────────────┐            │
       │              │  Dependency     │◀───────────┘
       │              │   Analyzer      │
       │              └────────┬────────┘
       │                       │
       │                       ▼
       │              ┌─────────────────┐
       └──────────────│  Visualization  │
                      │     Data        │
                      │   (JSON/Graph)  │
                      └─────────────────┘
```

---

## 🎬 User Workflows

### Workflow 1: Explore New Project

```
1. User navigates to "Code Explorer" tab
2. Click "Analyze Project" button
3. Backend scans all files (progress bar shown)
4. Bubble graph rendered with all files
5. User sees overview: which files are central
6. Click on largest bubble (usually main entry point)
7. Sidebar shows file details + functions
8. User navigates through dependency tree
```

### Workflow 2: Find Function Usage

```
1. User searches for function name "create_app"
2. System highlights files containing this function
3. User clicks on app.py bubble
4. Sidebar shows create_app() details
5. "Called by" section lists all usages
6. User clicks on a caller to see context
```

### Workflow 3: Refactoring Safety Check

```
1. User wants to change function signature
2. Searches for function in explorer
3. Sees "Called by: 23 locations"
4. Reviews all call sites
5. Decides if safe to refactor
6. Uses "Export to TODO list" for tracking
```

### Workflow 4: Dead Code Detection

```
1. User runs "Find Unused Code" analysis
2. System highlights files/functions with 0 imports
3. User reviews candidates for deletion
4. Marks some as "intentional dead code" (tests, examples)
5. Exports cleanup report
```

---

## 📊 Data & Performance Considerations

### Scalability Limits

| Project Size | Files | Functions | Rendering Time | Memory |
|:------------|------:|----------:|---------------:|-------:|
| Small       | < 100 | < 500     | < 1s           | ~50MB  |
| Medium      | < 500 | < 2,000   | < 3s           | ~200MB |
| Large       | < 2000| < 10,000  | < 10s          | ~500MB |
| Huge        | 2000+ | 10,000+   | 10s+           | 1GB+   |

### Performance Optimizations

1. **Lazy Loading** - Parse files on-demand
2. **Caching** - Cache parsed results in JSON
3. **Progressive Rendering** - Show partial results while scanning
4. **WebWorkers** - Offload graph calculations to background thread
5. **Virtual Scrolling** - For large function lists
6. **Graph Simplification** - Group related files into clusters

### Caching Strategy

```python
# Cache structure
cache/
├── project_hash_abc123/
│   ├── files.json          # All parsed files
│   ├── dependencies.json   # Dependency graph
│   ├── functions.json      # Function index
│   └── metadata.json       # Last scan time, config
```

**Cache Invalidation:**
- File modification time changed
- New files added/removed
- Manual "Refresh" button
- Cache older than 24 hours

---

## 🚀 MVP Features (Phase 1)

### Must Have
- ✅ Parse Python files only (using AST)
- ✅ Extract functions and imports
- ✅ Build file-level dependency graph
- ✅ Render basic bubble graph (D3.js)
- ✅ Click to show file details
- ✅ Show functions list in sidebar
- ✅ Basic filtering (by name)

### Nice to Have
- ⭐ Multi-language support (JS, TS)
- ⭐ Function-level call graph
- ⭐ "Imported by" reverse lookup
- ⭐ Dead code detection
- ⭐ Export to various formats

### Future (Phase 2+)
- 🔮 Real-time updates (watch mode)
- 🔮 Code complexity metrics (cyclomatic)
- 🔮 AI-powered insights ("This file is too complex")
- 🔮 Diff view (compare before/after refactor)
- 🔮 Integration with Git history

---

## 🛠️ Implementation Plan

### Week 1: Backend Foundation
- [x] Create `server/visualizer/` module structure
- [x] Implement Python AST parser
- [x] Build basic dependency analyzer
- [x] Create API endpoints
- [x] Write unit tests

### Week 2: Frontend Prototype
- [x] Set up D3.js bubble graph
- [x] Create basic force layout
- [x] Implement zoom & pan
- [x] Build details sidebar component
- [x] Add click interactions

### Week 3: Integration & Polish
- [ ] Connect frontend to backend API
- [ ] Add loading states & error handling
- [ ] Implement caching system
- [ ] Performance testing with large projects
- [ ] UI/UX refinements

### Week 4: Testing & Documentation
- [ ] User testing with 5 friends
- [ ] Fix bugs & edge cases
- [ ] Write documentation
- [ ] Create demo video
- [ ] Prepare for release

---

## 📝 Technical Decisions to Discuss

### 1. **Language Support Priority**
   - Start with Python only? (easiest, 80% of our users)
   - Or multi-language from day 1? (more complex, better UX)
   
   **Recommendation:** Python-only MVP, add JS/TS in Phase 2
   We use python-only mvp for now

### 2. **Graph Library Choice**
   - D3.js (full control, steep learning curve)
   - Cytoscape.js (easier, less customization)
   - Vis.js (batteries-included, heavier)
   
   **Recommendation:** D3.js for flexibility

   use D3.js

### 3. **Caching Strategy**
   - File-based cache (simple, slower)
   - SQLite database (faster, more complex)
   - In-memory only (fast, lost on restart)
   
   **Recommendation:** File-based JSON for MVP
   Use filebased

### 4. **Backend Parsing**
   - Python AST (built-in, Python only)
   - Tree-sitter (universal, complex setup)
   - Language-specific parsers (best accuracy)
   
   **Recommendation:** Python AST for MVP

   use python ast

### 5. **UI Layout**
   - Separate page (cleaner, more space)
   - Tab in existing UI (consistent, less context switch)
   
   **Recommendation:** New tab "Code Explorer" in existing UI
   New Tab

---

## 🎨 Design Mockups Needed

### Priority Mockups:
1. **Main bubble graph view** (with sample project)
2. **File details sidebar** (expanded state)
3. **Function details modal** (with call graph)
4. **Filter panel** (all filter options)
5. **Settings panel** (layout, color scheme, etc)

---

## 🧪 Testing Strategy

### Unit Tests
- Parser extracts correct functions
- Dependency analyzer builds valid graph
- API returns correct JSON

### Integration Tests
- Full scan of sample project
- Cache invalidation works
- Frontend renders graph correctly

### User Testing Questions
1. Can you find the main entry point?
2. How would you find all usages of function X?
3. Is the graph layout intuitive?
4. What features are missing?
5. Performance acceptable for your project size?

---

## 📈 Success Metrics

### Quantitative
- ✅ Parse 1000+ file project in < 10 seconds
- ✅ Render graph with 500+ nodes smoothly (60fps)
- ✅ Cache hit rate > 80%
- ✅ 70%+ of test users find it useful

### Qualitative
- ✅ Users can navigate unfamiliar codebase faster
- ✅ "Aha!" moments when seeing dependency structure
- ✅ Reduces time spent grepping for function usages
- ✅ Helps with refactoring confidence

---

## 🤔 Open Questions

1. **Should we visualize external dependencies** (npm packages, pip modules)?
   - Pro: Complete picture
   - Con: Graph becomes cluttered

   Dont di this
   
2. **How to handle very large projects** (10,000+ files)?
   - Option A: Folder-level grouping
   - Option B: Focus mode (show subset)
   - Option C: Hierarchical clustering

   Use Option B
   
3. **Should we store historical data** (track metrics over time)?
   - Could show "file complexity trend"
   - Requires database, more complex

   No Need for now
   
4. **Collaboration features?**
   - Share visualization links
   - Annotations on files/functions
   - Team insights

   No Need for now

5. **Integration with existing tools?**
   - VS Code extension?
   - GitHub integration?
   - CI/CD pipeline reports?

   No Need for now

---

## 💰 Business Model Ideas

### For CodeExplorer as Separate Product:

**Free Tier:**
- ✅ Projects up to 500 files
- ✅ Python only
- ✅ Local analysis only

**Pro Tier ($9/month):**
- ✅ Unlimited files
- ✅ All languages (JS, TS, Java, Go, etc.)
- ✅ Historical tracking
- ✅ Export reports
- ✅ Priority support

**Team Tier ($49/month):**
- ✅ Everything in Pro
- ✅ Shared visualizations
- ✅ Team insights & analytics
- ✅ SSO integration
- ✅ CI/CD integration

---

## 🎯 Next Steps

1. **Review this document** - Add comments, questions
2. **Prioritize features** - MVP vs Nice-to-Have
3. **Create design mockups** - Get visual clarity
4. **Spike: D3.js prototype** - Prove concept works
5. **Architecture review** - Validate technical approach
6. **Start implementation** - Begin Week 1 tasks

---

## 📚 References & Inspiration

### Similar Tools:
- **Sourcegraph** - Code navigation at scale
- **Understand** - Static code analysis tool
- **CodeSee** - Visual code maps
- **Madge** - Dependency graph for Node.js

### Technical Resources:
- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [D3.js Force Layout](https://d3js.org/d3-force)
- [Esprima JavaScript Parser](https://esprima.org/)
- [TypeScript Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API)

---

**Document Version:** 1.0  
**Last Updated:** October 26, 2025  
**Author:** Anwitch  
**Status:** 🟡 Draft - Ready for Discussion
