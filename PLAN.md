# CodeDevour → AI Feature Studio
## Technical Implementation Plan

**Version:** 2.0 Beta  
**Target Launch:** Q2 2026  
**Author:** Development Team  
**Last Updated:** February 9, 2026

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Target Architecture](#target-architecture)
4. [Implementation Phases](#implementation-phases)
5. [Technical Specifications](#technical-specifications)
6. [Database Schema](#database-schema)
7. [API Design](#api-design)
8. [Frontend Components](#frontend-components)
9. [AI Integration](#ai-integration)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Plan](#deployment-plan)
12. [Risk Mitigation](#risk-mitigation)

---

## 📊 Executive Summary

### Vision
Transform CodeDevour from a code visualization tool into an **AI-Powered Feature Studio** that enables developers to visually plan and automatically generate new features using context-aware AI.

### Key Differentiators
- ✅ Visual architecture + AI code generation
- ✅ Dependency graph-guided feature planning
- ✅ Multi-file context-aware generation
- ✅ Template-based rapid development
- ✅ Real-time validation & preview

### Success Metrics
| Metric | Target | Timeline |
|--------|--------|----------|
| Code acceptance rate | >70% | Month 3 |
| Generation time | <15s | Month 2 |
| User satisfaction (NPS) | >50 | Month 6 |
| Free→Pro conversion | 10% | Month 4 |

---

## 🔍 Current Codebase Status

### Status: February 9, 2026 Analysis

**File path references in this plan are CORRECT and match the actual codebase.**

---

### Existing Capabilities ✅

#### 1. Code Parsing & Analysis
```python
# Already implemented in server/visualizer/parser.py
Languages Supported: 13+ (Python, JS, TS, Java, C++, Go, Rust, PHP, Ruby, C#, Swift, Kotlin)
Parsing Depth:
  - Functions/Methods (with params, decorators, async detection)
  - Classes (with inheritance, methods)
  - Imports (module tracking)
  - Function calls within functions
```

#### 2. Dependency Graph
```javascript
// Already implemented in static/js/visualizer/BubbleGraph.js
Features:
  - D3.js force-directed graph
  - Centrality metrics (file importance)
  - Circular dependency detection
  - Interactive zoom/pan
  - File detail sidebar (DetailsSidebar.js)
```

#### 3. Infrastructure
```python
# Already implemented
- Async task processing (server/services/task_manager.py)
- Caching system (server/visualizer/cache_manager.py)
- Memory management
- Real-time progress tracking
- File streaming (128KB chunks)
```

#### 4. Visualizer Routes
```python
# Already implemented in server/routes/visualizer.py
Endpoints:
  - POST /api/visualizer/scan - Scan project and build graphs
  - GET /api/visualizer/graph - Get dependency graph data
  - GET /api/visualizer/file/<path> - Get file details
  - GET /api/visualizer/stats - Get project statistics
  - POST /api/visualizer/cache/clear - Clear cache
  - GET /visualizer - Render Code Explorer page
```

#### 5. Existing Frontend Components
```javascript
// Already implemented in static/js/visualizer/
- BubbleGraph.js - D3.js force-directed graph visualization
- DetailsSidebar.js - File detail sidebar
- FileTree.js - File tree navigation
- FilterPanel.js - Filter configuration panel
```

---

### Components to Create 🔴

| Component | Path | Status |
|-----------|------|--------|
| AI Module | `server/ai/` | **TO CREATE** |
| AI Routes | `server/routes/ai_routes.py` | **TO CREATE** |
| Feature Dialog HTML | `server/templates/CodeExplorer.html` | **TO ADD** |
| Feature Nodes JS | `static/js/visualizer/feature_nodes.js` | **TO CREATE** |
| Context Menu JS | `static/js/visualizer/context_menu.js` | **TO CREATE** |
| Code Preview Panel JS | `static/js/visualizer/code_preview_panel.js` | **TO CREATE** |
| Template Manager JS | `static/js/visualizer/template_manager.js` | **TO CREATE** |

---

### Gaps to Fill 🔴

1. **AI Integration Layer** - Not yet implemented
2. **Feature Planning UI** - Not yet implemented
3. **Code Generation Engine** - Not yet implemented
4. **Multi-file Integration Logic** - Not yet implemented
5. **Template System** - Not yet implemented
6. **Validation Pipeline** - Not yet implemented

---

## 🏗️ Target Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Code Graph   │  │ Feature      │  │ Code Preview │      │
│  │ Visualizer   │  │ Dialog       │  │ Panel        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │ REST API
┌──────────────────────────┼───────────────────────────────────┐
│                     Flask Backend                            │
│  ┌──────────────────────────────────────────────────┐       │
│  │              API Routes Layer                     │       │
│  │  /api/ai/*  |  /api/visualizer/*  |  /api/tasks/* │       │
│  └──────────────────────────────────────────────────┘       │
│         │                  │                  │              │
│  ┌──────▼──────┐  ┌───────▼──────┐  ┌────────▼──────┐      │
│  │ AI Service  │  │ Code Parser  │  │ Task Manager  │      │
│  │   Layer     │  │   Service    │  │   Service     │      │
│  └─────────────┘  └──────────────┘  └───────────────┘      │
│         │                  │                                 │
│         │         ┌────────▼────────┐                        │
│         │         │  Cache Manager  │                        │
│         │         └─────────────────┘                        │
│         │                                                    │
│  ┌──────▼─────────────────────────────────────────┐         │
│  │          External AI Services                   │         │
│  │  Anthropic Claude API  |  OpenAI GPT-4 API     │         │
│  └─────────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                    Persistence Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  PostgreSQL  │  │    Redis     │  │  File Cache  │       │
│  │  (Tasks,     │  │  (Sessions,  │  │  (Parsed     │       │
│  │   Projects)  │  │   Temp Data) │  │   Code)      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Frontend (React + D3.js)
- **Graph Canvas**: Enhanced D3 visualization with feature nodes
- **Feature Dialog**: Multi-step wizard for feature specification
- **Code Preview**: Monaco Editor integration with diff view
- **Validation Panel**: Real-time code quality checks

#### Backend (Python + Flask)
- **AI Service**: Context building, prompt engineering, code generation
- **Parser Service**: Multi-language code analysis (existing, enhanced)
- **Integration Service**: Smart code merging and file updates
- **Validation Service**: Syntax, security, pattern checks

#### Data Layer
- **PostgreSQL**: User projects, generation history, templates
- **Redis**: Session management, task queues, real-time updates
- **File Cache**: Parsed code metadata, dependency graphs

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Weeks 1-4)

#### Week 1: Backend AI Service Setup

**Tasks:**
1. Set up AI service infrastructure
2. Implement basic context builder
3. Create prompt templates
4. Test Claude API integration

**Deliverables:**
```python
# New files to create:
server/ai/
├── __init__.py
├── code_generator.py      # Main AI generation logic
├── context_builder.py     # Build context from codebase
├── prompt_templates.py    # Prompt engineering
├── validator.py           # Code validation
└── integrator.py         # Code integration logic

server/routes/
├── ai_routes.py          # New AI endpoints

requirements.txt
├── anthropic>=0.18.0     # Claude API
├── openai>=1.0.0         # GPT-4 API (backup)
└── tiktoken>=0.5.0       # Already exists
```

**Code Example: AI Service Foundation**
```python
# server/ai/code_generator.py

from anthropic import Anthropic
from typing import Dict, List, Optional
import json
from .context_builder import ContextBuilder
from .prompt_templates import PromptTemplates
from .validator import CodeValidator

class AICodeGenerator:
    """Main AI code generation service"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.context_builder = ContextBuilder()
        self.prompt_templates = PromptTemplates()
        self.validator = CodeValidator()
        
    def generate_feature(self, feature_spec: Dict) -> Dict:
        """
        Generate code for a new feature
        
        Args:
            feature_spec = {
                'name': str,
                'type': 'api_endpoint' | 'service' | 'model' | 'component',
                'description': str,
                'connected_files': List[str],
                'input_schema': Dict,
                'output_schema': Dict,
                'framework': str,  # auto-detected
                'project_path': str
            }
            
        Returns:
            {
                'success': bool,
                'files': Dict[str, str],  # path -> content
                'integrations': Dict[str, str],  # file -> code to add
                'tests': Dict[str, str],  # optional test files
                'validation': Dict,
                'metadata': Dict
            }
        """
        
        try:
            # 1. Build context from codebase
            context = self.context_builder.build_context(
                project_path=feature_spec['project_path'],
                connected_files=feature_spec['connected_files'],
                feature_type=feature_spec['type']
            )
            
            # 2. Select appropriate prompt template
            prompt = self.prompt_templates.get_prompt(
                feature_type=feature_spec['type'],
                framework=feature_spec['framework']
            )
            
            # 3. Fill prompt with context and spec
            filled_prompt = prompt.format(
                feature_name=feature_spec['name'],
                description=feature_spec['description'],
                input_schema=json.dumps(feature_spec['input_schema'], indent=2),
                output_schema=json.dumps(feature_spec['output_schema'], indent=2),
                context=self._format_context(context),
                existing_patterns=context['patterns'],
                code_examples=context['examples']
            )
            
            # 4. Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                temperature=0.3,  # Lower for more consistent code
                messages=[{
                    "role": "user",
                    "content": filled_prompt
                }]
            )
            
            # 5. Parse AI response
            generated = self._parse_ai_response(response.content[0].text)
            
            # 6. Validate generated code
            validation = self.validator.validate(
                generated_code=generated['files'],
                framework=feature_spec['framework'],
                existing_code=context['existing_code']
            )
            
            # 7. Return results
            return {
                'success': validation['valid'],
                'files': generated['files'],
                'integrations': generated.get('integrations', {}),
                'tests': generated.get('tests', {}),
                'validation': validation,
                'metadata': {
                    'tokens_used': response.usage.total_tokens,
                    'model': response.model,
                    'timestamp': response.created_at
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files': {},
                'integrations': {},
                'tests': {},
                'validation': {'valid': False, 'errors': [str(e)]},
                'metadata': {}
            }
    
    def _format_context(self, context: Dict) -> str:
        """Format context for prompt"""
        formatted = []
        
        # Add architecture info
        formatted.append(f"Architecture: {context['architecture']['type']}")
        formatted.append(f"Framework: {context['architecture']['framework']}")
        
        # Add relevant code snippets
        if context['examples']:
            formatted.append("\nExisting Code Examples:")
            for example in context['examples'][:3]:  # Limit to 3 examples
                formatted.append(f"\n{example['file']}:")
                formatted.append(f"```{example['language']}")
                formatted.append(example['code'])
                formatted.append("```")
        
        return "\n".join(formatted)
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response to extract code"""
        # AI should return JSON with structure:
        # {
        #   "files": {"path": "content"},
        #   "integrations": {"file": "code"},
        #   "tests": {"path": "content"}
        # }
        
        try:
            # Remove markdown code fences if present
            cleaned = response_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            # Fallback: extract code blocks manually
            return self._fallback_parse(response_text)
    
    def _fallback_parse(self, text: str) -> Dict:
        """Fallback parser if JSON fails"""
        # Extract code blocks from markdown
        import re
        
        files = {}
        blocks = re.findall(r'```(\w+)\n# File: (.+?)\n(.*?)```', text, re.DOTALL)
        
        for lang, filepath, code in blocks:
            files[filepath] = code.strip()
        
        return {
            'files': files,
            'integrations': {},
            'tests': {}
        }
```

#### Week 2: Context Builder Implementation

**Code Example: Context Builder**
```python
# server/ai/context_builder.py

import os
from typing import Dict, List
from pathlib import Path
from server.visualizer.parser import CodeParser
from server.visualizer.dependency_analyzer import DependencyAnalyzer

class ContextBuilder:
    """Build rich context for AI from codebase"""
    
    def __init__(self):
        self.parser = CodeParser()
        self.analyzer = DependencyAnalyzer()
    
    def build_context(
        self,
        project_path: str,
        connected_files: List[str],
        feature_type: str
    ) -> Dict:
        """
        Build comprehensive context for AI
        
        Returns:
            {
                'architecture': {...},
                'patterns': {...},
                'examples': [...],
                'existing_code': {...}
            }
        """
        
        context = {
            'architecture': self._detect_architecture(project_path),
            'patterns': self._extract_patterns(project_path, connected_files),
            'examples': self._get_relevant_examples(
                project_path, 
                connected_files, 
                feature_type
            ),
            'existing_code': self._parse_connected_files(
                project_path,
                connected_files
            )
        }
        
        return self._optimize_context(context)
    
    def _detect_architecture(self, project_path: str) -> Dict:
        """Detect project architecture and framework"""
        
        architecture = {
            'type': 'unknown',
            'framework': 'unknown',
            'language': 'unknown',
            'patterns': []
        }
        
        # Check for common files/folders
        project_root = Path(project_path)
        
        # Python frameworks
        if (project_root / 'app.py').exists() or (project_root / 'manage.py').exists():
            architecture['language'] = 'python'
            
            # Check for Flask
            if self._file_contains(project_root / 'requirements.txt', 'flask'):
                architecture['framework'] = 'flask'
                architecture['type'] = 'mvc' if (project_root / 'models').exists() else 'simple'
            
            # Check for Django
            elif (project_root / 'manage.py').exists():
                architecture['framework'] = 'django'
                architecture['type'] = 'mvt'
            
            # Check for FastAPI
            elif self._file_contains(project_root / 'requirements.txt', 'fastapi'):
                architecture['framework'] = 'fastapi'
                architecture['type'] = 'rest_api'
        
        # JavaScript/TypeScript frameworks
        elif (project_root / 'package.json').exists():
            architecture['language'] = 'javascript'
            
            package_json = self._read_json(project_root / 'package.json')
            deps = {**package_json.get('dependencies', {}), 
                    **package_json.get('devDependencies', {})}
            
            if 'next' in deps:
                architecture['framework'] = 'nextjs'
                architecture['type'] = 'ssr'
            elif 'react' in deps:
                architecture['framework'] = 'react'
                architecture['type'] = 'spa'
            elif 'vue' in deps:
                architecture['framework'] = 'vue'
                architecture['type'] = 'spa'
            elif 'express' in deps:
                architecture['framework'] = 'express'
                architecture['type'] = 'rest_api'
        
        return architecture
    
    def _extract_patterns(self, project_path: str, connected_files: List[str]) -> Dict:
        """Extract coding patterns from existing code"""
        
        patterns = {
            'naming': self._analyze_naming_conventions(project_path),
            'imports': self._analyze_import_patterns(connected_files),
            'error_handling': self._analyze_error_patterns(connected_files),
            'structure': self._analyze_folder_structure(project_path),
            'formatting': self._detect_formatter(project_path)
        }
        
        return patterns
    
    def _analyze_naming_conventions(self, project_path: str) -> Dict:
        """Analyze how things are named in the project"""
        
        conventions = {
            'functions': [],
            'classes': [],
            'files': [],
            'variables': []
        }
        
        # Sample files to analyze
        sample_files = self._get_sample_files(project_path, max_files=10)
        
        for file_path in sample_files:
            parsed = self.parser.parse_file(file_path)
            
            # Collect function names
            for func in parsed.get('functions', []):
                conventions['functions'].append(func['name'])
            
            # Collect class names
            for cls in parsed.get('classes', []):
                conventions['classes'].append(cls['name'])
        
        # Detect patterns
        detected = {
            'function_case': self._detect_case_style(conventions['functions']),
            'class_case': self._detect_case_style(conventions['classes']),
            'file_case': 'snake_case' if '_' in str(sample_files[0]) else 'kebab-case'
        }
        
        return detected
    
    def _get_relevant_examples(
        self,
        project_path: str,
        connected_files: List[str],
        feature_type: str
    ) -> List[Dict]:
        """Get relevant code examples similar to what we're generating"""
        
        examples = []
        
        if feature_type == 'api_endpoint':
            # Find existing API endpoints
            examples = self._find_api_endpoints(project_path)
        
        elif feature_type == 'service':
            # Find existing service classes
            examples = self._find_service_classes(project_path)
        
        elif feature_type == 'model':
            # Find existing models
            examples = self._find_models(project_path)
        
        elif feature_type == 'component':
            # Find existing components
            examples = self._find_components(project_path)
        
        # Limit to top 3 most relevant
        return examples[:3]
    
    def _find_api_endpoints(self, project_path: str) -> List[Dict]:
        """Find existing API endpoints as examples"""
        
        endpoints = []
        project_root = Path(project_path)
        
        # Common API route file patterns
        route_patterns = ['**/routes/**/*.py', '**/api/**/*.py', '**/views/**/*.py']
        
        for pattern in route_patterns:
            for file_path in project_root.glob(pattern):
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Find Flask routes
                if '@app.route' in content or '@bp.route' in content:
                    endpoints.append({
                        'file': str(file_path.relative_to(project_root)),
                        'language': 'python',
                        'code': self._extract_function_with_decorator(
                            content,
                            ['@app.route', '@bp.route']
                        ),
                        'type': 'flask_endpoint'
                    })
                
                # Find FastAPI routes
                elif '@app.get' in content or '@router.get' in content:
                    endpoints.append({
                        'file': str(file_path.relative_to(project_root)),
                        'language': 'python',
                        'code': self._extract_function_with_decorator(
                            content,
                            ['@app.get', '@router.get', '@app.post']
                        ),
                        'type': 'fastapi_endpoint'
                    })
        
        return endpoints
    
    def _optimize_context(self, context: Dict) -> Dict:
        """Optimize context to fit within token limits"""
        
        # Target: ~30K tokens for context
        # Strategy: Prioritize recent/relevant code, summarize older code
        
        MAX_EXAMPLE_LENGTH = 1000  # chars per example
        
        # Truncate long examples
        if context['examples']:
            for example in context['examples']:
                if len(example['code']) > MAX_EXAMPLE_LENGTH:
                    example['code'] = example['code'][:MAX_EXAMPLE_LENGTH] + '\n# ... (truncated)'
        
        return context
    
    # Helper methods
    
    def _file_contains(self, filepath: Path, text: str) -> bool:
        """Check if file contains text"""
        if not filepath.exists():
            return False
        try:
            return text.lower() in filepath.read_text(encoding='utf-8', errors='ignore').lower()
        except:
            return False
    
    def _read_json(self, filepath: Path) -> Dict:
        """Read JSON file"""
        import json
        try:
            return json.loads(filepath.read_text(encoding='utf-8'))
        except:
            return {}
    
    def _detect_case_style(self, names: List[str]) -> str:
        """Detect naming convention from list of names"""
        if not names:
            return 'unknown'
        
        snake_count = sum(1 for n in names if '_' in n and n.islower())
        camel_count = sum(1 for n in names if n[0].islower() and any(c.isupper() for c in n))
        pascal_count = sum(1 for n in names if n[0].isupper())
        
        counts = {'snake_case': snake_count, 'camelCase': camel_count, 'PascalCase': pascal_count}
        return max(counts, key=counts.get)
    
    def _get_sample_files(self, project_path: str, max_files: int = 10) -> List[Path]:
        """Get sample files from project"""
        project_root = Path(project_path)
        files = []
        
        for ext in ['.py', '.js', '.ts', '.jsx', '.tsx']:
            files.extend(list(project_root.glob(f'**/*{ext}'))[:max_files])
            if len(files) >= max_files:
                break
        
        return files[:max_files]
    
    def _parse_connected_files(self, project_path: str, connected_files: List[str]) -> Dict:
        """Parse connected files for detailed context"""
        parsed = {}
        
        for file_path in connected_files:
            full_path = Path(project_path) / file_path
            if full_path.exists():
                parsed[file_path] = self.parser.parse_file(str(full_path))
        
        return parsed
    
    def _extract_function_with_decorator(self, content: str, decorators: List[str]) -> str:
        """Extract function with specific decorators"""
        lines = content.split('\n')
        result = []
        capturing = False
        indent_level = 0
        
        for i, line in enumerate(lines):
            # Check for decorator
            if any(dec in line for dec in decorators):
                capturing = True
                result.append(line)
                continue
            
            if capturing:
                # Capture decorator and function
                if line.strip().startswith('def '):
                    indent_level = len(line) - len(line.lstrip())
                    result.append(line)
                elif line.strip() and not line.startswith(' ' * (indent_level + 1)):
                    # End of function
                    break
                else:
                    result.append(line)
        
        return '\n'.join(result[:20])  # Limit to 20 lines
```

#### Week 3: Prompt Templates

**Code Example: Prompt Templates**
```python
# server/ai/prompt_templates.py

class PromptTemplates:
    """Prompt engineering templates for different feature types"""
    
    def get_prompt(self, feature_type: str, framework: str) -> str:
        """Get appropriate prompt template"""
        
        templates = {
            'api_endpoint': self._api_endpoint_prompt,
            'service': self._service_layer_prompt,
            'model': self._model_prompt,
            'component': self._component_prompt
        }
        
        template_func = templates.get(feature_type, self._generic_prompt)
        return template_func(framework)
    
    def _api_endpoint_prompt(self, framework: str) -> str:
        """Prompt for generating API endpoints"""
        
        if framework == 'flask':
            return """You are an expert Flask backend developer. Generate code for a new API endpoint.

CODEBASE CONTEXT:
{context}

EXISTING PATTERNS:
{existing_patterns}

FEATURE REQUIREMENTS:
- Feature Name: {feature_name}
- Description: {description}
- Input Schema:
{input_schema}
- Output Schema:
{output_schema}

EXISTING CODE EXAMPLES:
{code_examples}

CRITICAL INSTRUCTIONS:
1. Follow the EXACT naming conventions shown in existing code
2. Use the SAME error handling patterns
3. Match the response format structure
4. Include all necessary imports
5. Add type hints (Flask 2.0+ style)
6. Include docstrings
7. Add input validation
8. Handle errors gracefully

OUTPUT FORMAT:
Return ONLY valid JSON with this structure (no markdown, no explanations):
{{
  "files": {{
    "path/to/new_file.py": "# Complete file content here\\n..."
  }},
  "integrations": {{
    "app.py": "# Code to add to app.py\\nfrom routes.new_route import new_blueprint\\napp.register_blueprint(new_blueprint)",
    "routes/__init__.py": "# Any init updates\\nfrom .new_route import new_blueprint"
  }},
  "tests": {{
    "tests/test_new_feature.py": "# Test file content\\n..."
  }}
}}

Generate production-ready code that integrates seamlessly with the existing codebase."""

        elif framework == 'fastapi':
            return """You are an expert FastAPI backend developer. Generate code for a new API endpoint.

CODEBASE CONTEXT:
{context}

EXISTING PATTERNS:
{existing_patterns}

FEATURE REQUIREMENTS:
- Feature Name: {feature_name}
- Description: {description}
- Input Schema (Pydantic):
{input_schema}
- Output Schema (Pydantic):
{output_schema}

EXISTING CODE EXAMPLES:
{code_examples}

CRITICAL INSTRUCTIONS:
1. Use Pydantic models for request/response
2. Follow existing naming conventions
3. Include proper type hints (Python 3.9+)
4. Add OpenAPI documentation (summary, description, tags)
5. Use async/await if database operations
6. Include proper exception handling
7. Add validation for inputs
8. Follow RESTful conventions

OUTPUT FORMAT:
Return ONLY valid JSON (no markdown):
{{
  "files": {{
    "routes/feature_name.py": "from fastapi import APIRouter, HTTPException\\n...",
    "models/feature_name.py": "from pydantic import BaseModel\\n...",
    "services/feature_name_service.py": "# Business logic\\n..."
  }},
  "integrations": {{
    "main.py": "from routes.feature_name import router\\napp.include_router(router, prefix='/api', tags=['Feature'])"
  }},
  "tests": {{
    "tests/test_feature_name.py": "from fastapi.testclient import TestClient\\n..."
  }}
}}

Generate production-ready, async-compatible code."""

        elif framework == 'express':
            return """You are an expert Node.js/Express backend developer. Generate code for a new API endpoint.

CODEBASE CONTEXT:
{context}

EXISTING PATTERNS:
{existing_patterns}

FEATURE REQUIREMENTS:
- Feature Name: {feature_name}
- Description: {description}
- Input Schema:
{input_schema}
- Output Schema:
{output_schema}

EXISTING CODE EXAMPLES:
{code_examples}

CRITICAL INSTRUCTIONS:
1. Use Express Router
2. Follow existing project structure
3. Include input validation (express-validator or Joi)
4. Add proper error handling middleware
5. Use async/await for async operations
6. Include JSDoc comments
7. Follow existing naming conventions
8. Add proper HTTP status codes

OUTPUT FORMAT:
Return ONLY valid JSON (no markdown):
{{
  "files": {{
    "routes/featureName.js": "const express = require('express');\\n...",
    "controllers/featureNameController.js": "// Controller logic\\n...",
    "middleware/featureNameValidation.js": "// Validation middleware\\n..."
  }},
  "integrations": {{
    "app.js": "const featureNameRoutes = require('./routes/featureName');\\napp.use('/api/feature', featureNameRoutes);"
  }},
  "tests": {{
    "tests/featureName.test.js": "const request = require('supertest');\\n..."
  }}
}}

Generate production-ready, well-structured code."""

        else:
            return self._generic_api_prompt()
    
    def _service_layer_prompt(self, framework: str) -> str:
        """Prompt for generating service layer code"""
        
        return """You are an expert software architect. Generate a service layer class/module.

CODEBASE CONTEXT:
{context}

EXISTING PATTERNS:
{existing_patterns}

SERVICE REQUIREMENTS:
- Service Name: {feature_name}
- Description: {description}
- Methods Needed:
{input_schema}
- Return Types:
{output_schema}

EXISTING SERVICE EXAMPLES:
{code_examples}

CRITICAL INSTRUCTIONS:
1. Follow Single Responsibility Principle
2. Use dependency injection for testability
3. Include proper error handling
4. Add logging at appropriate levels
5. Make methods testable (pure functions where possible)
6. Include type hints/interfaces
7. Follow existing service patterns exactly
8. Add comprehensive docstrings

OUTPUT FORMAT (JSON only):
{{
  "files": {{
    "services/feature_service.py": "class FeatureService:\\n    def __init__(self, dependencies):\\n..."
  }},
  "integrations": {{
    "existing_service.py": "from services.feature_service import FeatureService\\nself.feature_service = FeatureService(deps)"
  }},
  "tests": {{
    "tests/test_feature_service.py": "import unittest\\n..."
  }}
}}"""
    
    def _model_prompt(self, framework: str) -> str:
        """Prompt for generating data models"""
        
        if framework == 'django':
            return """You are an expert Django developer. Generate a Django model.

CODEBASE CONTEXT:
{context}

EXISTING MODELS:
{code_examples}

MODEL REQUIREMENTS:
- Model Name: {feature_name}
- Description: {description}
- Fields:
{input_schema}
- Relationships:
{output_schema}

INSTRUCTIONS:
1. Use Django ORM best practices
2. Include proper Meta class
3. Add __str__ method
4. Include validators where appropriate
5. Follow existing naming conventions
6. Add proper indexes
7. Include docstrings

OUTPUT FORMAT (JSON):
{{
  "files": {{
    "models/feature_model.py": "from django.db import models\\n...",
    "migrations/0001_add_feature.py": "# Migration file\\n..."
  }},
  "integrations": {{
    "models/__init__.py": "from .feature_model import FeatureModel"
  }}
}}"""
        
        elif framework == 'sqlalchemy':
            return """You are an expert SQLAlchemy developer. Generate a SQLAlchemy model.

CODEBASE CONTEXT:
{context}

EXISTING MODELS:
{code_examples}

MODEL REQUIREMENTS:
- Model Name: {feature_name}
- Description: {description}
- Columns:
{input_schema}
- Relationships:
{output_schema}

INSTRUCTIONS:
1. Use declarative base
2. Include proper column types
3. Add relationships with backref
4. Include __repr__ method
5. Follow existing patterns
6. Add constraints where needed

OUTPUT FORMAT (JSON):
{{
  "files": {{
    "models/feature.py": "from sqlalchemy import Column, Integer, String\\n..."
  }},
  "integrations": {{
    "models/__init__.py": "from .feature import Feature"
  }}
}}"""
        
        else:
            return self._generic_model_prompt()
    
    def _component_prompt(self, framework: str) -> str:
        """Prompt for generating UI components"""
        
        if framework == 'react':
            return """You are an expert React developer. Generate a React component.

CODEBASE CONTEXT:
{context}

EXISTING COMPONENTS:
{code_examples}

COMPONENT REQUIREMENTS:
- Component Name: {feature_name}
- Description: {description}
- Props:
{input_schema}
- State/Output:
{output_schema}

INSTRUCTIONS:
1. Use functional components with hooks
2. Follow existing component structure
3. Include PropTypes or TypeScript types
4. Add proper error handling
5. Make component reusable
6. Include comments for complex logic
7. Follow existing styling approach (CSS modules/styled-components/Tailwind)

OUTPUT FORMAT (JSON):
{{
  "files": {{
    "components/FeatureName.jsx": "import React, {{ useState }} from 'react';\\n...",
    "components/FeatureName.css": "/* Component styles */\\n..."
  }},
  "integrations": {{
    "components/index.js": "export {{ default as FeatureName }} from './FeatureName';"
  }},
  "tests": {{
    "components/__tests__/FeatureName.test.jsx": "import {{ render, screen }} from '@testing-library/react';\\n..."
  }}
}}"""
        
        elif framework == 'vue':
            return """You are an expert Vue.js developer. Generate a Vue component.

CODEBASE CONTEXT:
{context}

EXISTING COMPONENTS:
{code_examples}

COMPONENT REQUIREMENTS:
- Component Name: {feature_name}
- Description: {description}
- Props:
{input_schema}
- Emits/Data:
{output_schema}

INSTRUCTIONS:
1. Use Composition API (Vue 3) if project uses it, else Options API
2. Follow existing component structure
3. Include prop validation
4. Add proper event handling
5. Make component reusable
6. Follow existing styling approach

OUTPUT FORMAT (JSON):
{{
  "files": {{
    "components/FeatureName.vue": "<template>\\n  <div>...</div>\\n</template>\\n..."
  }},
  "integrations": {{
    "components/index.js": "export {{ default as FeatureName }} from './FeatureName.vue';"
  }}
}}"""
        
        else:
            return self._generic_component_prompt()
    
    def _generic_prompt(self) -> str:
        """Fallback generic prompt"""
        return """Generate code based on the following requirements:

FEATURE: {feature_name}
DESCRIPTION: {description}

INPUT: {input_schema}
OUTPUT: {output_schema}

CONTEXT: {context}
EXAMPLES: {code_examples}

Return valid JSON with 'files', 'integrations', and 'tests' keys."""
```

#### Week 4: Validator Implementation

**Code Example: Code Validator**
```python
# server/ai/validator.py

import ast
import re
from typing import Dict, List
import subprocess
from pathlib import Path

class CodeValidator:
    """Validate AI-generated code"""
    
    def validate(
        self,
        generated_code: Dict[str, str],
        framework: str,
        existing_code: Dict
    ) -> Dict:
        """
        Run comprehensive validation on generated code
        
        Returns:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'suggestions': List[str],
                'checks': Dict[str, bool]
            }
        """
        
        checks = {
            'syntax': self._check_syntax(generated_code),
            'security': self._check_security(generated_code),
            'patterns': self._check_consistency(generated_code, existing_code),
            'imports': self._check_imports(generated_code),
            'formatting': self._check_formatting(generated_code, framework)
        }
        
        errors = []
        warnings = []
        suggestions = []
        
        # Collect errors from failed checks
        for check_name, result in checks.items():
            if not result['passed']:
                errors.extend(result.get('errors', []))
                warnings.extend(result.get('warnings', []))
                suggestions.extend(result.get('suggestions', []))
        
        return {
            'valid': all(check['passed'] for check in checks.values()),
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions,
            'checks': {k: v['passed'] for k, v in checks.items()}
        }
    
    def _check_syntax(self, generated_code: Dict[str, str]) -> Dict:
        """Check for syntax errors"""
        
        errors = []
        
        for filepath, content in generated_code.items():
            ext = Path(filepath).suffix
            
            if ext == '.py':
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append(f"Syntax error in {filepath}: {e.msg} at line {e.lineno}")
            
            elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                # Use esprima or acorn for JS validation (if installed)
                try:
                    result = subprocess.run(
                        ['node', '-c'],
                        input=content.encode(),
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode != 0:
                        errors.append(f"Syntax error in {filepath}")
                except:
                    pass  # Skip if node not available
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def _check_security(self, generated_code: Dict[str, str]) -> Dict:
        """Check for common security issues"""
        
        warnings = []
        
        security_patterns = {
            'sql_injection': r'SELECT.*?FROM.*?\+|f"SELECT.*?FROM',
            'command_injection': r'os\.system|subprocess\.call\(',
            'hardcoded_secrets': r'password\s*=\s*["\'][^"\']+["\']|api_key\s*=\s*["\'][^"\']+["\']',
            'unsafe_eval': r'\beval\(',
            'xss_risk': r'innerHTML\s*=|dangerouslySetInnerHTML'
        }
        
        for filepath, content in generated_code.items():
            for issue, pattern in security_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    warnings.append(f"Potential {issue.replace('_', ' ')} in {filepath}")
        
        return {
            'passed': True,  # Warnings don't fail validation
            'warnings': warnings,
            'suggestions': [
                'Review security warnings before applying code',
                'Use parameterized queries for database operations',
                'Use environment variables for secrets'
            ] if warnings else []
        }
    
    def _check_consistency(
        self,
        generated_code: Dict[str, str],
        existing_code: Dict
    ) -> Dict:
        """Check if generated code follows existing patterns"""
        
        warnings = []
        suggestions = []
        
        # Check naming conventions
        existing_func_names = []
        for file_data in existing_code.values():
            for func in file_data.get('functions', []):
                existing_func_names.append(func['name'])
        
        if existing_func_names:
            # Detect case style
            snake_case_count = sum(1 for n in existing_func_names if '_' in n)
            camel_case_count = sum(1 for n in existing_func_names 
                                   if n[0].islower() and any(c.isupper() for c in n))
            
            expected_case = 'snake_case' if snake_case_count > camel_case_count else 'camelCase'
            
            # Check generated code
            for filepath, content in generated_code.items():
                if Path(filepath).suffix == '.py':
                    func_pattern = r'def\s+(\w+)\s*\('
                    funcs = re.findall(func_pattern, content)
                    
                    for func_name in funcs:
                        if expected_case == 'snake_case' and not self._is_snake_case(func_name):
                            warnings.append(
                                f"Function '{func_name}' in {filepath} doesn't follow snake_case convention"
                            )
                        elif expected_case == 'camelCase' and self._is_snake_case(func_name):
                            warnings.append(
                                f"Function '{func_name}' in {filepath} doesn't follow camelCase convention"
                            )
        
        return {
            'passed': len(warnings) == 0,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _check_imports(self, generated_code: Dict[str, str]) -> Dict:
        """Check if all imports are valid"""
        
        errors = []
        warnings = []
        
        for filepath, content in generated_code.items():
            ext = Path(filepath).suffix
            
            if ext == '.py':
                # Find all imports
                import_pattern = r'^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))'
                imports = re.findall(import_pattern, content, re.MULTILINE)
                
                for from_module, import_module in imports:
                    module = from_module or import_module
                    
                    # Check if it's a standard library or common package
                    if module and not self._is_known_module(module):
                        warnings.append(
                            f"Unknown import '{module}' in {filepath}. "
                            f"Make sure this package is installed."
                        )
        
        return {
            'passed': len(errors) == 0,
            'warnings': warnings
        }
    
    def _check_formatting(self, generated_code: Dict[str, str], framework: str) -> Dict:
        """Check code formatting"""
        
        suggestions = []
        
        for filepath, content in generated_code.items():
            ext = Path(filepath).suffix
            
            if ext == '.py':
                # Check line length
                long_lines = [
                    i + 1 for i, line in enumerate(content.split('\n'))
                    if len(line) > 100
                ]
                if long_lines:
                    suggestions.append(
                        f"{filepath}: Lines {long_lines[:3]} exceed 100 characters. "
                        f"Consider breaking them up."
                    )
                
                # Check for docstrings
                if 'def ' in content and '"""' not in content and "'''" not in content:
                    suggestions.append(
                        f"{filepath}: Consider adding docstrings to functions"
                    )
        
        return {
            'passed': True,  # Formatting issues are just suggestions
            'suggestions': suggestions
        }
    
    # Helper methods
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name is snake_case"""
        return '_' in name and name.islower()
    
    def _is_known_module(self, module: str) -> bool:
        """Check if module is a known standard library or common package"""
        
        stdlib = {
            'os', 'sys', 're', 'json', 'time', 'datetime', 'collections',
            'typing', 'pathlib', 'subprocess', 'threading', 'asyncio'
        }
        
        common_packages = {
            'flask', 'fastapi', 'django', 'requests', 'numpy', 'pandas',
            'sqlalchemy', 'pydantic', 'pytest', 'unittest'
        }
        
        base_module = module.split('.')[0]
        return base_module in stdlib or base_module in common_packages
```

**Deliverables Week 4:**
- Complete AI service backend
- All validation logic
- API routes for AI features
- Unit tests for core AI functionality

---

### Phase 2: Frontend Integration (Weeks 5-8)

#### Week 5: Enhanced Graph Visualization

**New Files:**
```
static/js/visualizer/
├── feature_nodes.js      # Feature node handling
├── context_menu.js       # Right-click context menu
└── node_connector.js     # Node connection logic
```

**Code Example: Feature Nodes**
```javascript
// static/js/visualizer/feature_nodes.js

class FeatureNodeManager {
    constructor(graph) {
        this.graph = graph;
        this.featureNodes = [];
        this.connections = [];
    }
    
    /**
     * Add a new feature node to the graph
     */
    addFeatureNode(spec) {
        const node = {
            id: `feature_${Date.now()}`,
            type: 'feature_planned',
            name: spec.name,
            description: spec.description,
            featureType: spec.type,  // 'api_endpoint', 'service', etc.
            x: spec.x || window.innerWidth / 2,
            y: spec.y || window.innerHeight / 2,
            fx: null,  // Allow dragging
            fy: null,
            connections: [],
            metadata: {
                inputSchema: spec.inputSchema || {},
                outputSchema: spec.outputSchema || {},
                createdAt: new Date().toISOString()
            }
        };
        
        this.featureNodes.push(node);
        this.graph.addNode(node);
        
        return node;
    }
    
    /**
     * Connect feature node to existing files
     */
    connectToFile(featureNodeId, fileNodeId) {
        const connection = {
            id: `conn_${Date.now()}`,
            source: featureNodeId,
            target: fileNodeId,
            type: 'planned_dependency',
            createdAt: new Date().toISOString()
        };
        
        this.connections.push(connection);
        this.graph.addEdge(connection);
        
        // Update feature node's connections list
        const featureNode = this.featureNodes.find(n => n.id === featureNodeId);
        if (featureNode) {
            featureNode.connections.push(fileNodeId);
        }
        
        return connection;
    }
    
    /**
     * Convert feature node to generation request
     */
    toGenerationRequest(featureNodeId) {
        const featureNode = this.featureNodes.find(n => n.id === featureNodeId);
        if (!featureNode) return null;
        
        // Get connected file paths
        const connectedFiles = featureNode.connections.map(fileId => {
            const fileNode = this.graph.getNode(fileId);
            return fileNode ? fileNode.id : null;
        }).filter(Boolean);
        
        return {
            name: featureNode.name,
            type: featureNode.featureType,
            description: featureNode.description,
            connected_files: connectedFiles,
            input_schema: featureNode.metadata.inputSchema,
            output_schema: featureNode.metadata.outputSchema,
            project_path: window.currentProjectPath
        };
    }
    
    /**
     * Update feature node after successful generation
     */
    markAsGenerated(featureNodeId, generatedFiles) {
        const node = this.featureNodes.find(n => n.id === featureNodeId);
        if (!node) return;
        
        node.type = 'feature_generated';
        node.metadata.generatedAt = new Date().toISOString();
        node.metadata.generatedFiles = generatedFiles;
        
        this.graph.updateNode(node);
    }
    
    /**
     * Remove feature node
     */
    removeFeatureNode(featureNodeId) {
        // Remove connections
        this.connections = this.connections.filter(c => 
            c.source !== featureNodeId && c.target !== featureNodeId
        );
        
        // Remove from graph
        this.graph.removeNode(featureNodeId);
        
        // Remove from local storage
        this.featureNodes = this.featureNodes.filter(n => n.id !== featureNodeId);
    }
}

// Export
window.FeatureNodeManager = FeatureNodeManager;
```

**Code Example: Context Menu**
```javascript
// static/js/visualizer/context_menu.js

class ContextMenu {
    constructor() {
        this.menuElement = null;
        this.currentTarget = null;
        this.init();
    }
    
    init() {
        // Create menu element
        this.menuElement = document.createElement('div');
        this.menuElement.id = 'context-menu';
        this.menuElement.className = 'absolute hidden bg-white rounded-lg shadow-xl border border-gray-200 z-50 py-2 min-w-[200px]';
        document.body.appendChild(this.menuElement);
        
        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!this.menuElement.contains(e.target)) {
                this.hide();
            }
        });
    }
    
    /**
     * Show context menu for a node
     */
    show(event, node, options = {}) {
        event.preventDefault();
        event.stopPropagation();
        
        this.currentTarget = node;
        
        // Build menu items based on node type
        const menuItems = this.getMenuItems(node, options);
        
        // Clear existing menu
        this.menuElement.innerHTML = '';
        
        // Add menu items
        menuItems.forEach(item => {
            if (item.separator) {
                const separator = document.createElement('div');
                separator.className = 'h-px bg-gray-200 my-1';
                this.menuElement.appendChild(separator);
            } else {
                const menuItem = document.createElement('div');
                menuItem.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-2 text-sm';
                menuItem.innerHTML = `
                    <span class="text-lg">${item.icon}</span>
                    <span>${item.label}</span>
                `;
                menuItem.onclick = () => {
                    item.action(node);
                    this.hide();
                };
                this.menuElement.appendChild(menuItem);
            }
        });
        
        // Position menu
        const x = event.pageX;
        const y = event.pageY;
        
        // Adjust position if menu would go off-screen
        const menuRect = this.menuElement.getBoundingClientRect();
        const adjustedX = (x + menuRect.width > window.innerWidth) 
            ? x - menuRect.width 
            : x;
        const adjustedY = (y + menuRect.height > window.innerHeight) 
            ? y - menuRect.height 
            : y;
        
        this.menuElement.style.left = `${adjustedX}px`;
        this.menuElement.style.top = `${adjustedY}px`;
        this.menuElement.classList.remove('hidden');
    }
    
    hide() {
        this.menuElement.classList.add('hidden');
        this.currentTarget = null;
    }
    
    /**
     * Get menu items based on node type
     */
    getMenuItems(node, options) {
        const items = [];
        
        if (node.type === 'file') {
            // Menu for existing file nodes
            items.push({
                icon: '✨',
                label: 'Add Related Feature',
                action: (n) => this.openFeatureDialog(n, 'related')
            });
            items.push({
                icon: '🔗',
                label: 'Add API Endpoint',
                action: (n) => this.openFeatureDialog(n, 'api_endpoint')
            });
            items.push({
                icon: '⚙️',
                label: 'Add Service Layer',
                action: (n) => this.openFeatureDialog(n, 'service')
            });
            items.push({
                icon: '🧪',
                label: 'Generate Tests',
                action: (n) => this.generateTests(n)
            });
            items.push({ separator: true });
            items.push({
                icon: '🔍',
                label: 'View Details',
                action: (n) => this.viewNodeDetails(n)
            });
            items.push({
                icon: '📊',
                label: 'Analyze Dependencies',
                action: (n) => this.analyzeDependencies(n)
            });
        } else if (node.type === 'feature_planned') {
            // Menu for planned feature nodes
            items.push({
                icon: '🚀',
                label: 'Generate Code',
                action: (n) => this.generateFeatureCode(n)
            });
            items.push({
                icon: '📝',
                label: 'Edit Specification',
                action: (n) => this.editFeatureSpec(n)
            });
            items.push({ separator: true });
            items.push({
                icon: '❌',
                label: 'Remove Feature',
                action: (n) => this.removeFeature(n)
            });
        } else if (node.type === 'feature_generated') {
            // Menu for generated feature nodes
            items.push({
                icon: '👁️',
                label: 'View Generated Code',
                action: (n) => this.viewGeneratedCode(n)
            });
            items.push({
                icon: '🔄',
                label: 'Regenerate',
                action: (n) => this.regenerateCode(n)
            });
            items.push({ separator: true });
            items.push({
                icon: '✅',
                label: 'Apply to Project',
                action: (n) => this.applyToProject(n)
            });
        }
        
        return items;
    }
    
    // Action handlers
    
    openFeatureDialog(node, type) {
        if (window.featureDialog) {
            window.featureDialog.open({
                type: type,
                connectedFile: node.id
            });
        }
    }
    
    generateTests(node) {
        // Trigger test generation for this file
        window.dispatchEvent(new CustomEvent('generate-tests', {
            detail: { fileNode: node }
        }));
    }
    
    viewNodeDetails(node) {
        // Show details in sidebar
        if (window.sidebarManager) {
            window.sidebarManager.showDetails(node);
        }
    }
    
    analyzeDependencies(node) {
        // Highlight dependencies in graph
        if (window.graphManager) {
            window.graphManager.highlightDependencies(node.id);
        }
    }
    
    generateFeatureCode(node) {
        // Trigger code generation
        window.dispatchEvent(new CustomEvent('generate-feature', {
            detail: { featureNode: node }
        }));
    }
    
    editFeatureSpec(node) {
        if (window.featureDialog) {
            window.featureDialog.edit(node);
        }
    }
    
    removeFeature(node) {
        if (confirm(`Remove feature "${node.name}"?`)) {
            if (window.featureNodeManager) {
                window.featureNodeManager.removeFeatureNode(node.id);
            }
        }
    }
    
    viewGeneratedCode(node) {
        if (window.codePreviewPanel) {
            window.codePreviewPanel.show(node.metadata.generatedFiles);
        }
    }
    
    regenerateCode(node) {
        if (confirm('Regenerate code for this feature?')) {
            this.generateFeatureCode(node);
        }
    }
    
    applyToProject(node) {
        window.dispatchEvent(new CustomEvent('apply-generated-code', {
            detail: { featureNode: node }
        }));
    }
}

// Initialize
window.contextMenu = new ContextMenu();
```

#### Week 6: Feature Dialog UI

**Note:** Feature Dialog HTML should be added to `server/templates/CodeExplorer.html`

**Code Example: Feature Dialog**
```html
<!-- Add to server/templates/CodeExplorer.html -->

<div id="feature-dialog" class="fixed inset-0 bg-black bg-opacity-50 hidden z-50 flex items-center justify-center">
    <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        <!-- Header -->
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">
                ✨ Create New Feature
            </h2>
            <button id="close-feature-dialog" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        
        <!-- Content -->
        <div class="p-6">
            <!-- Step 1: Feature Type Selection -->
            <div id="step-type" class="step-content">
                <h3 class="text-lg font-semibold mb-4">Select Feature Type</h3>
                <div class="grid grid-cols-2 gap-4">
                    <button class="feature-type-btn border-2 border-gray-300 rounded-lg p-6 hover:border-blue-500 hover:bg-blue-50 transition-all" data-type="api_endpoint">
                        <div class="text-4xl mb-2">🌐</div>
                        <div class="font-semibold">API Endpoint</div>
                        <div class="text-sm text-gray-600 mt-2">Create a new REST API endpoint</div>
                    </button>
                    
                    <button class="feature-type-btn border-2 border-gray-300 rounded-lg p-6 hover:border-blue-500 hover:bg-blue-50 transition-all" data-type="service">
                        <div class="text-4xl mb-2">⚙️</div>
                        <div class="font-semibold">Service Layer</div>
                        <div class="text-sm text-gray-600 mt-2">Add business logic service</div>
                    </button>
                    
                    <button class="feature-type-btn border-2 border-gray-300 rounded-lg p-6 hover:border-blue-500 hover:bg-blue-50 transition-all" data-type="model">
                        <div class="text-4xl mb-2">📦</div>
                        <div class="font-semibold">Data Model</div>
                        <div class="text-sm text-gray-600 mt-2">Create database model/entity</div>
                    </button>
                    
                    <button class="feature-type-btn border-2 border-gray-300 rounded-lg p-6 hover:border-blue-500 hover:bg-blue-50 transition-all" data-type="component">
                        <div class="text-4xl mb-2">🎨</div>
                        <div class="font-semibold">UI Component</div>
                        <div class="text-sm text-gray-600 mt-2">Generate React/Vue component</div>
                    </button>
                </div>
            </div>
            
            <!-- Step 2: Feature Specification -->
            <div id="step-spec" class="step-content hidden">
                <h3 class="text-lg font-semibold mb-4">Feature Specification</h3>
                
                <div class="space-y-4">
                    <!-- Feature Name -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Feature Name
                        </label>
                        <input type="text" id="feature-name" 
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                               placeholder="e.g., UserAuthentication, PaymentProcessor">
                    </div>
                    
                    <!-- Description -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Description
                        </label>
                        <textarea id="feature-description" rows="3"
                                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                  placeholder="Describe what this feature should do..."></textarea>
                    </div>
                    
                    <!-- Input Schema Builder -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Input Schema
                            <span class="text-xs text-gray-500">(Parameters/Props)</span>
                        </label>
                        <div id="input-schema-builder" class="border border-gray-300 rounded-lg p-4">
                            <div class="flex gap-2 mb-2">
                                <input type="text" placeholder="Field name" class="flex-1 px-3 py-2 border border-gray-300 rounded" id="input-field-name">
                                <select class="px-3 py-2 border border-gray-300 rounded" id="input-field-type">
                                    <option value="string">String</option>
                                    <option value="number">Number</option>
                                    <option value="boolean">Boolean</option>
                                    <option value="object">Object</option>
                                    <option value="array">Array</option>
                                </select>
                                <input type="checkbox" id="input-field-required" class="mt-2">
                                <label for="input-field-required" class="mt-2 text-sm">Required</label>
                                <button id="add-input-field" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                                    Add
                                </button>
                            </div>
                            <div id="input-fields-list" class="space-y-2">
                                <!-- Fields will be added here -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Output Schema Builder -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Output Schema
                            <span class="text-xs text-gray-500">(Return type/Response)</span>
                        </label>
                        <div id="output-schema-builder" class="border border-gray-300 rounded-lg p-4">
                            <div class="flex gap-2 mb-2">
                                <input type="text" placeholder="Field name" class="flex-1 px-3 py-2 border border-gray-300 rounded" id="output-field-name">
                                <select class="px-3 py-2 border border-gray-300 rounded" id="output-field-type">
                                    <option value="string">String</option>
                                    <option value="number">Number</option>
                                    <option value="boolean">Boolean</option>
                                    <option value="object">Object</option>
                                    <option value="array">Array</option>
                                </select>
                                <button id="add-output-field" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                                    Add
                                </button>
                            </div>
                            <div id="output-fields-list" class="space-y-2">
                                <!-- Fields will be added here -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Connected Files -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Related Files
                            <span class="text-xs text-gray-500">(Files this feature depends on)</span>
                        </label>
                        <div id="connected-files-list" class="border border-gray-300 rounded-lg p-4 min-h-[100px]">
                            <p class="text-sm text-gray-500">
                                Click on files in the graph to connect them to this feature
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Step 3: Review & Generate -->
            <div id="step-review" class="step-content hidden">
                <h3 class="text-lg font-semibold mb-4">Review & Generate</h3>
                
                <div id="feature-summary" class="bg-gray-50 rounded-lg p-6">
                    <!-- Summary will be populated here -->
                </div>
                
                <div class="mt-6">
                    <h4 class="font-semibold mb-2">AI will generate:</h4>
                    <ul class="list-disc list-inside space-y-1 text-sm text-gray-700">
                        <li>New files with complete implementation</li>
                        <li>Integration code for existing files</li>
                        <li>Basic unit tests</li>
                        <li>Documentation comments</li>
                    </ul>
                </div>
                
                <div id="generation-progress" class="hidden mt-6">
                    <div class="flex items-center gap-3">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                        <div>
                            <div class="font-semibold">Generating code...</div>
                            <div id="generation-status" class="text-sm text-gray-600">
                                Analyzing codebase...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex items-center justify-between">
            <button id="dialog-back-btn" class="px-4 py-2 text-gray-700 hover:text-gray-900 hidden">
                ← Back
            </button>
            <div class="flex gap-2">
                <button id="dialog-cancel-btn" class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    Cancel
                </button>
                <button id="dialog-next-btn" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
                    Next →
                </button>
                <button id="dialog-generate-btn" class="hidden px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                    ✨ Generate Code
                </button>
            </div>
        </div>
    </div>
</div>
```

**JavaScript for Feature Dialog:**
```javascript
// static/js/visualizer/feature_dialog.js

class FeatureDialog {
    constructor() {
        this.currentStep = 1;
        this.featureData = {
            type: null,
            name: '',
            description: '',
            inputSchema: {},
            outputSchema: {},
            connectedFiles: []
        };
        this.init();
    }
    
    init() {
        // Get DOM elements
        this.dialog = document.getElementById('feature-dialog');
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Close button
        document.getElementById('close-feature-dialog').addEventListener('click', () => {
            this.close();
        });
        
        // Feature type buttons
        document.querySelectorAll('.feature-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.featureData.type = e.currentTarget.dataset.type;
                this.highlightSelectedType(e.currentTarget);
                document.getElementById('dialog-next-btn').disabled = false;
            });
        });
        
        // Navigation buttons
        document.getElementById('dialog-next-btn').addEventListener('click', () => {
            this.nextStep();
        });
        
        document.getElementById('dialog-back-btn').addEventListener('click', () => {
            this.previousStep();
        });
        
        document.getElementById('dialog-cancel-btn').addEventListener('click', () => {
            this.close();
        });
        
        document.getElementById('dialog-generate-btn').addEventListener('click', () => {
            this.generateCode();
        });
        
        // Schema builders
        this.setupSchemaBuilder('input');
        this.setupSchemaBuilder('output');
    }
    
    setupSchemaBuilder(type) {
        const addBtn = document.getElementById(`add-${type}-field`);
        const nameInput = document.getElementById(`${type}-field-name`);
        const typeSelect = document.getElementById(`${type}-field-type`);
        const requiredCheckbox = type === 'input' ? document.getElementById(`${type}-field-required`) : null;
        const fieldsList = document.getElementById(`${type}-fields-list`);
        
        addBtn.addEventListener('click', () => {
            const fieldName = nameInput.value.trim();
            const fieldType = typeSelect.value;
            const required = requiredCheckbox ? requiredCheckbox.checked : false;
            
            if (!fieldName) return;
            
            // Add to schema
            const schemaKey = `${type}Schema`;
            this.featureData[schemaKey][fieldName] = {
                type: fieldType,
                required: required
            };
            
            // Add to UI
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'flex items-center justify-between bg-white px-3 py-2 rounded border border-gray-200';
            fieldDiv.innerHTML = `
                <div class="flex items-center gap-2">
                    <span class="font-mono text-sm">${fieldName}</span>
                    <span class="text-xs text-gray-500">${fieldType}</span>
                    ${required ? '<span class="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded">required</span>' : ''}
                </div>
                <button class="text-red-500 hover:text-red-700" onclick="this.closest('[class*=flex]').remove()">
                    ×
                </button>
            `;
            fieldsList.appendChild(fieldDiv);
            
            // Clear inputs
            nameInput.value = '';
            if (requiredCheckbox) requiredCheckbox.checked = false;
        });
    }
    
    open(options = {}) {
        this.dialog.classList.remove('hidden');
        this.currentStep = 1;
        this.showStep(1);
        
        // Pre-fill if options provided
        if (options.type) {
            this.featureData.type = options.type;
        }
        if (options.connectedFile) {
            this.featureData.connectedFiles = [options.connectedFile];
        }
    }
    
    close() {
        this.dialog.classList.add('hidden');
        this.reset();
    }
    
    reset() {
        this.currentStep = 1;
        this.featureData = {
            type: null,
            name: '',
            description: '',
            inputSchema: {},
            outputSchema: {},
            connectedFiles: []
        };
        
        // Clear form
        document.getElementById('feature-name').value = '';
        document.getElementById('feature-description').value = '';
        document.getElementById('input-fields-list').innerHTML = '';
        document.getElementById('output-fields-list').innerHTML = '';
    }
    
    nextStep() {
        if (this.currentStep === 1) {
            if (!this.featureData.type) {
                alert('Please select a feature type');
                return;
            }
        } else if (this.currentStep === 2) {
            // Validate step 2
            const name = document.getElementById('feature-name').value.trim();
            if (!name) {
                alert('Please enter a feature name');
                return;
            }
            this.featureData.name = name;
            this.featureData.description = document.getElementById('feature-description').value.trim();
            
            // Show summary
            this.showSummary();
        }
        
        this.currentStep++;
        this.showStep(this.currentStep);
    }
    
    previousStep() {
        this.currentStep--;
        this.showStep(this.currentStep);
    }
    
    showStep(step) {
        // Hide all steps
        document.querySelectorAll('.step-content').forEach(el => {
            el.classList.add('hidden');
        });
        
        // Show current step
        const stepId = ['step-type', 'step-spec', 'step-review'][step - 1];
        document.getElementById(stepId).classList.remove('hidden');
        
        // Update buttons
        const backBtn = document.getElementById('dialog-back-btn');
        const nextBtn = document.getElementById('dialog-next-btn');
        const generateBtn = document.getElementById('dialog-generate-btn');
        
        backBtn.classList.toggle('hidden', step === 1);
        nextBtn.classList.toggle('hidden', step === 3);
        generateBtn.classList.toggle('hidden', step !== 3);
    }
    
    showSummary() {
        const summaryDiv = document.getElementById('feature-summary');
        const typeLabels = {
            api_endpoint: '🌐 API Endpoint',
            service: '⚙️ Service Layer',
            model: '📦 Data Model',
            component: '🎨 UI Component'
        };
        
        summaryDiv.innerHTML = `
            <div class="space-y-4">
                <div>
                    <div class="text-sm text-gray-600">Type</div>
                    <div class="font-semibold">${typeLabels[this.featureData.type]}</div>
                </div>
                <div>
                    <div class="text-sm text-gray-600">Name</div>
                    <div class="font-semibold">${this.featureData.name}</div>
                </div>
                <div>
                    <div class="text-sm text-gray-600">Description</div>
                    <div>${this.featureData.description || '<em>No description</em>'}</div>
                </div>
                <div>
                    <div class="text-sm text-gray-600">Input Fields</div>
                    <div class="font-mono text-sm bg-white rounded p-2 mt-1">
                        ${JSON.stringify(this.featureData.inputSchema, null, 2)}
                    </div>
                </div>
                <div>
                    <div class="text-sm text-gray-600">Output Fields</div>
                    <div class="font-mono text-sm bg-white rounded p-2 mt-1">
                        ${JSON.stringify(this.featureData.outputSchema, null, 2)}
                    </div>
                </div>
                <div>
                    <div class="text-sm text-gray-600">Connected Files</div>
                    <div>${this.featureData.connectedFiles.length} files</div>
                </div>
            </div>
        `;
    }
    
    async generateCode() {
        const progressDiv = document.getElementById('generation-progress');
        const statusDiv = document.getElementById('generation-status');
        const generateBtn = document.getElementById('dialog-generate-btn');
        
        progressDiv.classList.remove('hidden');
        generateBtn.disabled = true;
        
        try {
            // Call AI generation API
            statusDiv.textContent = 'Building context from codebase...';
            
            const response = await fetch('/api/ai/generate-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.featureData)
            });
            
            if (!response.ok) {
                throw new Error('Generation failed');
            }
            
            statusDiv.textContent = 'Generating code with AI...';
            
            const result = await response.json();
            
            if (result.success) {
                statusDiv.textContent = 'Validating generated code...';
                
                // Show preview
                this.showCodePreview(result);
                this.close();
            } else {
                throw new Error(result.error || 'Generation failed');
            }
            
        } catch (error) {
            alert('Error generating code: ' + error.message);
        } finally {
            progressDiv.classList.add('hidden');
            generateBtn.disabled = false;
        }
    }
    
    showCodePreview(generatedCode) {
        // Trigger code preview panel
        window.dispatchEvent(new CustomEvent('show-code-preview', {
            detail: generatedCode
        }));
    }
    
    highlightSelectedType(button) {
        document.querySelectorAll('.feature-type-btn').forEach(btn => {
            btn.classList.remove('border-blue-500', 'bg-blue-50');
            btn.classList.add('border-gray-300');
        });
        button.classList.remove('border-gray-300');
        button.classList.add('border-blue-500', 'bg-blue-50');
    }
}

// Initialize
window.featureDialog = new FeatureDialog();
```

#### Week 7: Code Preview Panel

**New Component:**
```
static/js/visualizer/
└── code_preview_panel.js
```

**Code Example:**
```javascript
// static/js/visualizer/code_preview_panel.js

class CodePreviewPanel {
    constructor() {
        this.currentFiles = {};
        this.currentValidation = {};
        this.selectedTab = null;
        this.init();
    }
    
    init() {
        this.panel = document.getElementById('code-preview-panel');
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        window.addEventListener('show-code-preview', (e) => {
            this.show(e.detail);
        });
        
        document.getElementById('preview-close-btn').addEventListener('click', () => {
            this.hide();
        });
        
        document.getElementById('preview-apply-btn').addEventListener('click', () => {
            this.applyChanges();
        });
        
        document.getElementById('preview-reject-btn').addEventListener('click', () => {
            this.rejectChanges();
        });
        
        document.getElementById('preview-regenerate-btn').addEventListener('click', () => {
            this.regenerate();
        });
    }
    
    show(generatedData) {
        this.currentFiles = generatedData.files;
        this.currentValidation = generatedData.validation;
        
        this.panel.classList.remove('hidden');
        this.renderFileTabs();
        this.renderValidation();
        this.selectFirstTab();
    }
    
    hide() {
        this.panel.classList.add('hidden');
        this.currentFiles = {};
        this.currentValidation = {};
    }
    
    renderFileTabs() {
        const tabsContainer = document.getElementById('preview-file-tabs');
        tabsContainer.innerHTML = '';
        
        Object.keys(this.currentFiles).forEach((filepath, index) => {
            const tab = document.createElement('button');
            tab.className = 'px-4 py-2 text-sm font-medium border-b-2 border-transparent hover:border-blue-500 transition-colors';
            tab.textContent = filepath.split('/').pop();
            tab.title = filepath;
            tab.onclick = () => this.selectTab(filepath);
            tab.dataset.filepath = filepath;
            tabsContainer.appendChild(tab);
        });
    }
    
    selectTab(filepath) {
        this.selectedTab = filepath;
        
        // Update tab styles
        document.querySelectorAll('#preview-file-tabs button').forEach(btn => {
            if (btn.dataset.filepath === filepath) {
                btn.classList.add('border-blue-500', 'text-blue-600');
            } else {
                btn.classList.remove('border-blue-500', 'text-blue-600');
            }
        });
        
        // Show file content
        this.renderFileContent(filepath);
    }
    
    selectFirstTab() {
        const firstFile = Object.keys(this.currentFiles)[0];
        if (firstFile) {
            this.selectTab(firstFile);
        }
    }
    
    renderFileContent(filepath) {
        const contentDiv = document.getElementById('preview-code-content');
        const content = this.currentFiles[filepath];
        
        // Use Monaco Editor or simple pre
        contentDiv.innerHTML = `
            <div class="bg-gray-900 rounded p-4 overflow-auto" style="max-height: 60vh;">
                <pre><code class="language-${this.getLanguage(filepath)}">${this.escapeHtml(content)}</code></pre>
            </div>
        `;
        
        // Apply syntax highlighting if available
        if (window.Prism) {
            Prism.highlightAllUnder(contentDiv);
        }
    }
    
    renderValidation() {
        const validationDiv = document.getElementById('preview-validation');
        const v = this.currentValidation;
        
        const checksHtml = Object.entries(v.checks || {}).map(([name, passed]) => {
            const icon = passed ? '✓' : '✗';
            const color = passed ? 'text-green-600' : 'text-red-600';
            return `<li class="${color}">${icon} ${this.formatCheckName(name)}</li>`;
        }).join('');
        
        const errorsHtml = (v.errors || []).map(err => 
            `<li class="text-red-600">• ${err}</li>`
        ).join('');
        
        const warningsHtml = (v.warnings || []).map(warn => 
            `<li class="text-yellow-600">⚠ ${warn}</li>`
        ).join('');
        
        validationDiv.innerHTML = `
            <h4 class="font-semibold mb-2">Validation Results</h4>
            <ul class="space-y-1 text-sm mb-4">
                ${checksHtml}
            </ul>
            ${errorsHtml ? `<div class="mb-2"><strong>Errors:</strong><ul class="ml-4">${errorsHtml}</ul></div>` : ''}
            ${warningsHtml ? `<div><strong>Warnings:</strong><ul class="ml-4">${warningsHtml}</ul></div>` : ''}
        `;
    }
    
    async applyChanges() {
        if (!confirm('Apply generated code to project?')) return;
        
        try {
            const response = await fetch('/api/ai/apply-changes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    files: this.currentFiles
                })
            });
            
            if (!response.ok) throw new Error('Failed to apply changes');
            
            const result = await response.json();
            
            if (result.success) {
                alert('Code applied successfully!');
                this.hide();
                
                // Refresh visualizer
                window.location.reload();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            alert('Error applying changes: ' + error.message);
        }
    }
    
    rejectChanges() {
        if (confirm('Discard generated code?')) {
            this.hide();
        }
    }
    
    regenerate() {
        if (confirm('Regenerate code? Current preview will be lost.')) {
            this.hide();
            // Trigger regeneration
            window.dispatchEvent(new CustomEvent('regenerate-feature'));
        }
    }
    
    // Helpers
    getLanguage(filepath) {
        const ext = filepath.split('.').pop();
        const map = {
            'py': 'python',
            'js': 'javascript',
            'jsx': 'jsx',
            'ts': 'typescript',
            'tsx': 'tsx',
            'html': 'html',
            'css': 'css',
            'json': 'json'
        };
        return map[ext] || 'text';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatCheckName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
}

// Initialize
window.codePreviewPanel = new CodePreviewPanel();
```

**HTML Template for Code Preview:**
```html
<!-- Add to server/templates/CodeExplorer.html -->
<div id="code-preview-panel" class="fixed right-0 top-0 h-full w-1/2 bg-white shadow-2xl z-40 hidden transform transition-transform">
    <div class="flex flex-col h-full">
        <!-- Header -->
        <div class="bg-gray-800 text-white px-6 py-4 flex items-center justify-between">
            <h3 class="text-xl font-semibold">Generated Code Preview</h3>
            <button id="preview-close-btn" class="text-gray-300 hover:text-white">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        
        <!-- File Tabs -->
        <div id="preview-file-tabs" class="flex gap-2 px-6 py-2 border-b border-gray-200 overflow-x-auto">
            <!-- Tabs populated by JS -->
        </div>
        
        <!-- Code Content -->
        <div id="preview-code-content" class="flex-1 overflow-auto p-6">
            <!-- Code displayed here -->
        </div>
        
        <!-- Validation Panel -->
        <div id="preview-validation" class="border-t border-gray-200 p-6 bg-gray-50">
            <!-- Validation results -->
        </div>
        
        <!-- Actions -->
        <div class="border-t border-gray-200 p-6 flex gap-3 justify-end">
            <button id="preview-reject-btn" class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                ❌ Reject
            </button>
            <button id="preview-regenerate-btn" class="px-6 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600">
                🔄 Regenerate
            </button>
            <button id="preview-apply-btn" class="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                ✅ Apply Changes
            </button>
        </div>
    </div>
</div>
```

#### Week 8: Integration & Testing

**Tasks:**
1. Connect all UI components
2. Implement event flow
3. Add loading states
4. Error handling
5. Integration testing

**Event Flow Diagram:**
```
User Action → Feature Dialog → AI Service → Code Preview → Apply to Project

1. Right-click node → Context Menu
2. Select "Add Feature" → Feature Dialog opens
3. Fill specification → Click "Generate"
4. API call to /api/ai/generate-code
5. AI Service builds context
6. AI Service calls Claude API
7. Validator checks generated code
8. Response sent to frontend
9. Code Preview Panel opens
10. User reviews → Clicks "Apply"
11. API call to /api/ai/apply-changes
12. Files written to project
13. Graph refreshed
```

---

### Phase 3: Template System (Weeks 9-10)

#### Week 9: Template Engine

**New Files:**
```
server/ai/
├── template_engine.py
└── templates/
    ├── crud_api.json
    ├── authentication.json
    ├── file_upload.json
    └── payment_integration.json
```

**Code Example: Template Engine**
```python
# server/ai/template_engine.py

import json
from pathlib import Path
from typing import Dict, List
import copy

class TemplateEngine:
    """Manage and apply feature templates"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / 'templates'
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load all template definitions"""
        templates = {}
        
        if not self.templates_dir.exists():
            return templates
        
        for template_file in self.templates_dir.glob('*.json'):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    templates[template_data['id']] = template_data
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
        
        return templates
    
    def get_template(self, template_id: str) -> Dict:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {
                'id': t['id'],
                'name': t['name'],
                'description': t['description'],
                'category': t.get('category', 'general'),
                'frameworks': t.get('frameworks', [])
            }
            for t in self.templates.values()
        ]
    
    def apply_template(
        self,
        template_id: str,
        parameters: Dict,
        framework: str
    ) -> Dict:
        """
        Apply template with user parameters
        
        Returns feature specification ready for AI generation
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Check framework compatibility
        if framework not in template.get('frameworks', ['*']):
            raise ValueError(
                f"Template {template_id} not compatible with {framework}"
            )
        
        # Create feature spec from template
        spec = copy.deepcopy(template['specification'])
        
        # Apply parameter substitutions
        spec = self._substitute_parameters(spec, parameters)
        
        return spec
    
    def _substitute_parameters(self, spec: Dict, params: Dict) -> Dict:
        """Replace template variables with actual parameters"""
        
        def replace_in_value(value, params):
            if isinstance(value, str):
                # Replace {{variable}} with actual value
                for key, val in params.items():
                    value = value.replace(f"{{{{{key}}}}}", str(val))
                return value
            elif isinstance(value, dict):
                return {k: replace_in_value(v, params) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_in_value(item, params) for item in value]
            else:
                return value
        
        return replace_in_value(spec, params)
```

**Example Template: CRUD API**
```json
// server/ai/templates/crud_api.json
{
  "id": "crud_api",
  "name": "CRUD API Endpoints",
  "description": "Generate complete CRUD (Create, Read, Update, Delete) API endpoints for a model",
  "category": "api",
  "frameworks": ["flask", "fastapi", "express"],
  "icon": "📝",
  "parameters": [
    {
      "name": "model_name",
      "type": "string",
      "label": "Model Name",
      "description": "Name of the model (e.g., User, Product)",
      "required": true,
      "example": "Product"
    },
    {
      "name": "fields",
      "type": "object",
      "label": "Model Fields",
      "description": "Fields for the model",
      "required": true,
      "example": {
        "name": "string",
        "price": "number",
        "description": "string",
        "stock": "number"
      }
    },
    {
      "name": "table_name",
      "type": "string",
      "label": "Database Table Name",
      "description": "Name of database table",
      "required": false,
      "default": "{{model_name|lower}}s"
    }
  ],
  "specification": {
    "name": "{{model_name}}CRUD",
    "type": "api_endpoint",
    "description": "Complete CRUD operations for {{model_name}} model",
    "endpoints": [
      {
        "method": "POST",
        "path": "/api/{{model_name|lower}}s",
        "action": "create",
        "description": "Create new {{model_name}}"
      },
      {
        "method": "GET",
        "path": "/api/{{model_name|lower}}s",
        "action": "list",
        "description": "List all {{model_name}}s"
      },
      {
        "method": "GET",
        "path": "/api/{{model_name|lower}}s/{id}",
        "action": "get",
        "description": "Get {{model_name}} by ID"
      },
      {
        "method": "PUT",
        "path": "/api/{{model_name|lower}}s/{id}",
        "action": "update",
        "description": "Update {{model_name}}"
      },
      {
        "method": "DELETE",
        "path": "/api/{{model_name|lower}}s/{id}",
        "action": "delete",
        "description": "Delete {{model_name}}"
      }
    ],
    "input_schema": "{{fields}}",
    "output_schema": {
      "id": "number",
      "...": "{{fields}}",
      "created_at": "datetime",
      "updated_at": "datetime"
    },
    "generates": [
      "Model class/schema",
      "CRUD route handlers",
      "Validation logic",
      "Database operations",
      "API tests"
    ]
  }
}
```

**Example Template: Authentication**
```json
// server/ai/templates/authentication.json
{
  "id": "authentication",
  "name": "JWT Authentication",
  "description": "Add JWT-based authentication system with login, register, and token refresh",
  "category": "security",
  "frameworks": ["flask", "fastapi", "express"],
  "icon": "🔐",
  "parameters": [
    {
      "name": "user_model",
      "type": "string",
      "label": "User Model Name",
      "required": true,
      "default": "User"
    },
    {
      "name": "token_expiry",
      "type": "number",
      "label": "Token Expiry (hours)",
      "required": false,
      "default": 24
    },
    {
      "name": "include_refresh_token",
      "type": "boolean",
      "label": "Include Refresh Token?",
      "required": false,
      "default": true
    }
  ],
  "specification": {
    "name": "Authentication",
    "type": "api_endpoint",
    "description": "JWT authentication system",
    "endpoints": [
      {
        "method": "POST",
        "path": "/api/auth/register",
        "action": "register",
        "description": "Register new user"
      },
      {
        "method": "POST",
        "path": "/api/auth/login",
        "action": "login",
        "description": "Login and get tokens"
      },
      {
        "method": "POST",
        "path": "/api/auth/refresh",
        "action": "refresh",
        "description": "Refresh access token"
      }
    ],
    "generates": [
      "Authentication service",
      "JWT token handlers",
      "Password hashing utilities",
      "Auth middleware/decorators",
      "Login/register endpoints",
      "Tests"
    ]
  }
}
```

#### Week 10: Template UI Integration

**Add to Feature Dialog:**
```html
<!-- Template Selection Step -->
<div id="step-template" class="step-content hidden">
    <h3 class="text-lg font-semibold mb-4">Choose a Template (Optional)</h3>
    
    <div class="mb-4">
        <input type="text" id="template-search" 
               class="w-full px-4 py-2 border border-gray-300 rounded-lg"
               placeholder="Search templates...">
    </div>
    
    <div class="grid grid-cols-2 gap-4" id="template-list">
        <!-- Templates populated by JS -->
    </div>
    
    <div class="mt-4">
        <button id="skip-template-btn" class="text-sm text-gray-600 hover:text-gray-900">
            Skip template, create from scratch →
        </button>
    </div>
</div>

<!-- Template Parameters Step -->
<div id="step-template-params" class="step-content hidden">
    <h3 class="text-lg font-semibold mb-4">Configure Template</h3>
    
    <div id="template-params-form" class="space-y-4">
        <!-- Parameters populated dynamically -->
    </div>
</div>
```

**JavaScript for Templates:**
```javascript
// static/js/visualizer/template_manager.js

class TemplateManager {
    constructor() {
        this.templates = [];
        this.selectedTemplate = null;
        this.init();
    }
    
    async init() {
        await this.loadTemplates();
    }
    
    async loadTemplates() {
        try {
            const response = await fetch('/api/ai/templates');
            this.templates = await response.json();
            this.renderTemplateList();
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }
    
    renderTemplateList() {
        const listDiv = document.getElementById('template-list');
        if (!listDiv) return;
        
        listDiv.innerHTML = '';
        
        this.templates.forEach(template => {
            const card = document.createElement('div');
            card.className = 'template-card border-2 border-gray-300 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all';
            card.innerHTML = `
                <div class="text-3xl mb-2">${template.icon}</div>
                <div class="font-semibold">${template.name}</div>
                <div class="text-sm text-gray-600 mt-1">${template.description}</div>
                <div class="mt-2 flex flex-wrap gap-1">
                    ${template.frameworks.map(fw => 
                        `<span class="text-xs bg-gray-200 px-2 py-0.5 rounded">${fw}</span>`
                    ).join('')}
                </div>
            `;
            card.onclick = () => this.selectTemplate(template);
            listDiv.appendChild(card);
        });
    }
    
    selectTemplate(template) {
        this.selectedTemplate = template;
        this.highlightSelectedTemplate(template.id);
        this.showTemplateParams(template);
    }
    
    showTemplateParams(template) {
        const formDiv = document.getElementById('template-params-form');
        formDiv.innerHTML = '';
        
        template.parameters.forEach(param => {
            const fieldDiv = document.createElement('div');
            fieldDiv.innerHTML = `
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    ${param.label}
                    ${param.required ? '<span class="text-red-500">*</span>' : ''}
                </label>
                <p class="text-xs text-gray-500 mb-2">${param.description}</p>
                ${this.renderParamInput(param)}
            `;
            formDiv.appendChild(fieldDiv);
        });
        
        // Show template params step
        document.getElementById('step-template').classList.add('hidden');
        document.getElementById('step-template-params').classList.remove('hidden');
    }
    
    renderParamInput(param) {
        if (param.type === 'string') {
            return `<input type="text" 
                           name="${param.name}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                           placeholder="${param.example || ''}"
                           ${param.required ? 'required' : ''}
                           value="${param.default || ''}">`;
        } else if (param.type === 'number') {
            return `<input type="number" 
                           name="${param.name}"
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                           ${param.required ? 'required' : ''}
                           value="${param.default || ''}">`;
        } else if (param.type === 'boolean') {
            return `<input type="checkbox" 
                           name="${param.name}"
                           class="mr-2"
                           ${param.default ? 'checked' : ''}>`;
        } else if (param.type === 'object') {
            return `<textarea name="${param.name}" 
                              class="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
                              rows="6"
                              ${param.required ? 'required' : ''}
                              placeholder="${JSON.stringify(param.example, null, 2)}">${param.default ? JSON.stringify(param.default, null, 2) : ''}</textarea>`;
        }
    }
    
    getTemplateParameters() {
        const formDiv = document.getElementById('template-params-form');
        const inputs = formDiv.querySelectorAll('[name]');
        const params = {};
        
        inputs.forEach(input => {
            const name = input.getAttribute('name');
            let value;
            
            if (input.type === 'checkbox') {
                value = input.checked;
            } else if (input.tagName === 'TEXTAREA') {
                try {
                    value = JSON.parse(input.value);
                } catch {
                    value = input.value;
                }
            } else {
                value = input.value;
            }
            
            params[name] = value;
        });
        
        return params;
    }
    
    async applyTemplate() {
        if (!this.selectedTemplate) return null;
        
        const params = this.getTemplateParameters();
        
        try {
            const response = await fetch('/api/ai/apply-template', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_id: this.selectedTemplate.id,
                    parameters: params,
                    framework: window.detectedFramework
                })
            });
            
            if (!response.ok) throw new Error('Failed to apply template');
            
            const spec = await response.json();
            return spec;
            
        } catch (error) {
            console.error('Error applying template:', error);
            return null;
        }
    }
}

window.templateManager = new TemplateManager();
```

**API Endpoint for Templates:**
```python
# server/routes/ai_routes.py

from server.ai.template_engine import TemplateEngine

template_engine = TemplateEngine()

@app.route('/api/ai/templates', methods=['GET'])
def get_templates():
    """List all available templates"""
    templates = template_engine.list_templates()
    return jsonify(templates)

@app.route('/api/ai/apply-template', methods=['POST'])
def apply_template():
    """Apply template with parameters"""
    data = request.json
    template_id = data.get('template_id')
    parameters = data.get('parameters', {})
    framework = data.get('framework', 'flask')
    
    try:
        spec = template_engine.apply_template(
            template_id,
            parameters,
            framework
        )
        return jsonify(spec)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

---

### Phase 4: Polish & Optimization (Weeks 11-12)

#### Week 11: Performance Optimization

**Tasks:**
1. **Caching Strategy**
   - Cache parsed file metadata
   - Cache dependency graphs
   - Cache AI generation contexts

2. **Streaming Improvements**
   - Stream AI responses as they generate
   - Show real-time progress

3. **Memory Management**
   - Limit context size intelligently
   - Clean up old generation results

**Code Example: Smart Caching**
```python
# server/ai/cache_manager.py

from functools import lru_cache
import hashlib
import json
from pathlib import Path

class AICache:
    """Cache for AI-related operations"""
    
    def __init__(self, cache_dir='data/cache/ai'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_context_cache(self, project_path: str, files: List[str]) -> Optional[Dict]:
        """Get cached context for project + files"""
        cache_key = self._get_cache_key(project_path, files)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    
                # Check if cache is still valid (files haven't changed)
                if self._is_cache_valid(cached, project_path, files):
                    return cached['context']
            except:
                pass
        
        return None
    
    def set_context_cache(
        self,
        project_path: str,
        files: List[str],
        context: Dict
    ):
        """Cache context for future use"""
        cache_key = self._get_cache_key(project_path, files)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'context': context,
            'metadata': {
                'project_path': project_path,
                'files': files,
                'file_hashes': self._get_file_hashes(project_path, files),
                'cached_at': datetime.now().isoformat()
            }
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    
    def _get_cache_key(self, project_path: str, files: List[str]) -> str:
        """Generate cache key"""
        key_data = f"{project_path}:{'|'.join(sorted(files))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_file_hashes(self, project_path: str, files: List[str]) -> Dict[str, str]:
        """Get hash of each file for cache validation"""
        hashes = {}
        for file_path in files:
            full_path = Path(project_path) / file_path
            if full_path.exists():
                content = full_path.read_bytes()
                hashes[file_path] = hashlib.md5(content).hexdigest()
        return hashes
    
    def _is_cache_valid(
        self,
        cached: Dict,
        project_path: str,
        files: List[str]
    ) -> bool:
        """Check if cache is still valid"""
        cached_hashes = cached['metadata'].get('file_hashes', {})
        current_hashes = self._get_file_hashes(project_path, files)
        
        return cached_hashes == current_hashes
```

#### Week 12: Testing & Documentation

**Testing Strategy:**

1. **Unit Tests**
```python
# tests/test_ai_generator.py

import unittest
from server.ai.code_generator import AICodeGenerator
from server.ai.context_builder import ContextBuilder

class TestAICodeGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = AICodeGenerator(api_key='test_key')
    
    def test_generate_flask_endpoint(self):
        spec = {
            'name': 'UserProfile',
            'type': 'api_endpoint',
            'description': 'Get user profile',
            'connected_files': ['models/user.py'],
            'input_schema': {},
            'output_schema': {'user': 'object'},
            'framework': 'flask',
            'project_path': '/test/project'
        }
        
        # Mock AI response
        with patch.object(self.generator.client, 'messages') as mock:
            mock.create.return_value = self._mock_ai_response()
            
            result = self.generator.generate_feature(spec)
            
            self.assertTrue(result['success'])
            self.assertIn('routes/user_profile.py', result['files'])
    
    def _mock_ai_response(self):
        return MagicMock(
            content=[MagicMock(text=json.dumps({
                'files': {
                    'routes/user_profile.py': '# Generated code'
                }
            }))],
            usage=MagicMock(total_tokens=1000)
        )
```

2. **Integration Tests**
```python
# tests/test_feature_generation_flow.py

class TestFeatureGenerationFlow(unittest.TestCase):
    def test_full_crud_generation(self):
        """Test complete CRUD generation flow"""
        # 1. Apply template
        template_params = {
            'model_name': 'Product',
            'fields': {
                'name': 'string',
                'price': 'number'
            }
        }
        
        spec = template_engine.apply_template(
            'crud_api',
            template_params,
            'flask'
        )
        
        # 2. Generate code
        result = generator.generate_feature(spec)
        
        # 3. Validate
        self.assertTrue(result['success'])
        self.assertGreater(len(result['files']), 0)
        
        # 4. Check validation
        self.assertTrue(result['validation']['valid'])
```

---

## 📊 Database Schema

```sql
-- PostgreSQL Schema

-- Projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    path TEXT NOT NULL,
    framework VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feature generations table
CREATE TABLE feature_generations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    feature_name VARCHAR(255) NOT NULL,
    feature_type VARCHAR(50) NOT NULL,
    specification JSONB NOT NULL,
    generated_files JSONB,
    validation_results JSONB,
    status VARCHAR(20) DEFAULT 'pending', -- pending, success, failed
    applied BOOLEAN DEFAULT FALSE,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_at TIMESTAMP
);

-- Templates table (user-created custom templates)
CREATE TABLE user_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    specification JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generation history for analytics
CREATE TABLE generation_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    feature_type VARCHAR(50),
    success BOOLEAN,
    tokens_used INTEGER,
    generation_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_generations_project ON feature_generations(project_id);
CREATE INDEX idx_generations_status ON feature_generations(status);
CREATE INDEX idx_stats_user_date ON generation_stats(user_id, created_at);
```

---

## 🔐 Security Considerations

### 1. API Key Management
```python
# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Backup
    
    # Never log or expose API keys
    SENSITIVE_KEYS = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY']
```

### 2. Code Validation
- Always validate AI-generated code before applying
- Run security scanners (bandit, semgrep)
- Sandbox execution for tests

### 3. User Input Sanitization
```python
def sanitize_feature_name(name: str) -> str:
    """Sanitize feature names to prevent path traversal"""
    # Remove path separators
    name = name.replace('/', '').replace('\\', '')
    # Remove special characters
    name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    return name
```

---

## 📈 Metrics & Analytics

### Track These Metrics:

```python
# server/services/analytics_service.py

class AnalyticsService:
    """Track product metrics"""
    
    def track_generation(self, data: Dict):
        """Track code generation event"""
        metrics = {
            'feature_type': data['type'],
            'success': data['success'],
            'tokens_used': data['tokens'],
            'generation_time': data['duration'],
            'validation_passed': data['validation']['valid'],
            'code_applied': False,  # Updated when user applies
            'timestamp': datetime.now()
        }
        # Store in database
    
    def track_user_action(self, action: str, metadata: Dict):
        """Track user interactions"""
        events = {
            'feature_dialog_opened': {},
            'template_selected': {'template_id': ...},
            'code_generated': {'feature_name': ...},
            'code_applied': {'files_count': ...},
            'code_rejected': {'reason': ...}
        }
```

---

## 🎯 Success Criteria

### Month 1 (Foundation):
- [x] AI service functional
- [x] Context builder works for 3+ frameworks
- [x] Validation pipeline complete
- [ ] Can generate simple endpoint successfully

### Month 2 (UI):
- [ ] Feature dialog fully functional
- [ ] Code preview panel working
- [ ] Can add feature node to graph
- [ ] End-to-end flow works

### Month 3 (Templates):
- [ ] 5+ templates available
- [ ] Template system functional
- [ ] Users can apply templates successfully

### Launch Criteria:
- [ ] 80%+ code acceptance rate
- [ ] <15s generation time
- [ ] Works with Flask, FastAPI, Express
- [ ] 50+ beta users tested
- [ ] All critical bugs fixed

---

## 🚨 Risk Mitigation

### Technical Risks:

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| AI generates broken code | High | High | Multi-layer validation, manual review |
| Context too large for API | Medium | Medium | Smart context optimization, chunking |
| Slow generation time | Medium | High | Caching, streaming, async processing |
| Integration breaks existing code | High | Critical | Preview before apply, rollback feature |
| Framework detection fails | Low | Medium | Manual framework selection option |

### Business Risks:

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Low conversion rate | Medium | High | Strong value prop, generous free tier |
| High AI API costs | High | High | Rate limiting, tier-based limits |
| Competitors copy feature | High | Medium | Fast iteration, community, integrations |

---

## 📅 Development Timeline

```
Month 1: Foundation (Weeks 1-4)
├── Week 1: AI Service Setup ✓
├── Week 2: Context Builder ✓
├── Week 3: Prompt Templates ✓
└── Week 4: Validator ✓

Month 2: Frontend (Weeks 5-8)
├── Week 5: Graph Enhancement
├── Week 6: Feature Dialog
├── Week 7: Code Preview
└── Week 8: Integration Testing

Month 3: Templates (Weeks 9-10)
├── Week 9: Template Engine
└── Week 10: Template UI

Month 4: Polish (Weeks 11-12)
├── Week 11: Performance
└── Week 12: Testing & Docs

Month 5-6: Beta & Launch
├── Beta testing (2 weeks)
├── Bug fixes (2 weeks)
├── Marketing prep (2 weeks)
└── Public launch
```

---

## 🎓 Learning Resources for Team

### AI Prompt Engineering:
- Anthropic's Prompt Engineering Guide
- OpenAI Best Practices
- Few-shot learning techniques

### Code Generation:
- Tree-sitter for parsing
- AST manipulation
- Static analysis tools

### Frontend:
- D3.js Force Simulation
- React Context API
- Monaco Editor integration

---

## 📝 Next Steps

### Immediate (This Week):
1. Set up development environment
2. Get Claude API key
3. Test basic AI code generation
4. Create simple feature dialog prototype

### Short Term (This Month):
1. Complete AI service layer
2. Build context builder for Flask
3. Test generation on real projects
4. Get feedback from 5 developers

### Medium Term (Month 2-3):
1. Build full UI
2. Add 5 templates
3. Beta testing with 50 users
4. Iterate based on feedback

---

## 💰 Budget Estimates

### Development Costs:
- Developer time (3-4 months): You + team
- AI API costs (testing): $500-1000/month
- Infrastructure: $100/month (development)

### Launch Costs:
- Production infrastructure: $500/month
- Marketing: $2000-5000 (initial)
- Legal (terms, privacy): $1000

### Ongoing Costs:
- AI API (variable): $0.10-0.30 per generation
- Infrastructure: Scales with users
- Support: Time investment

---

**Document Status:** Draft v1.0  
**Last Updated:** February 9, 2026  
**Next Review:** Weekly during development

---

*This plan is a living document and will be updated as development progresses and requirements evolve.*
