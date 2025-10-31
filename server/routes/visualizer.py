"""
Visualizer API Routes

REST API endpoints for code visualization:
- POST /api/visualizer/scan - Scan project and build graphs
- GET /api/visualizer/graph - Get dependency graph data
- GET /api/visualizer/file/<path> - Get file details
- GET /api/visualizer/stats - Get project statistics
- POST /api/visualizer/cache/clear - Clear cache
- GET /visualizer - Render Code Explorer page
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template, current_app
from server.config import load_config, get_config
from server.visualizer import CodeParser, DependencyAnalyzer, CacheManager

visualizer_bp = Blueprint('visualizer', __name__)

# Initialize components
parser = CodeParser()
cache_manager = CacheManager()


@visualizer_bp.route('/api/visualizer/scan', methods=['POST'])
def scan_project():
    """
    Scan project and generate visualization data with config-based filtering
    
    Request body:
    {
        "project_path": "/path/to/project",  // optional, uses config if not provided
        "use_cache": true,                   // optional, default true
        "include_tests": false,              // optional, default false
        "force_refresh": false               // optional, default false
    }
    
    Returns:
    {
        "status": "success",
        "file_count": 42,
        "function_count": 156,
        "cached": false,
        "scan_time": 2.34,
        "filters_applied": {
            "exclude_patterns": 15,
            "just_me_patterns": 3,
            "total_files_scanned": 100
        }
    }
    """
    try:
        data = request.get_json()
        project_path = data.get('project_path')
        use_cache = data.get('use_cache', True)
        include_tests = data.get('include_tests', False)
        force_refresh = data.get('force_refresh', False)
        
        # Get config for filtering rules
        config = get_config()
        if not project_path:
            project_path = config.get('TARGET_FOLDER')
        
        if not project_path or not os.path.exists(project_path):
            return jsonify({
                'status': 'error',
                'message': 'Invalid project path'
            }), 400
        
        project_path = os.path.abspath(project_path)
        
        # Load filtering patterns from config
        exclude_file = config.get("EXCLUDE_FILE_PATH")
        just_me_file = config.get("JUST_ME_FILE_PATH")
        
        # Read filtering patterns
        exclude_patterns = set()
        if exclude_file and os.path.exists(exclude_file):
            try:
                with open(exclude_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped and not stripped.startswith('#'):
                            exclude_patterns.add(stripped)
            except Exception as e:
                print(f"Warning: Could not load exclude patterns: {e}")
        
        just_me_patterns = set()
        if just_me_file and os.path.exists(just_me_file):
            try:
                with open(just_me_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped and not stripped.startswith('#'):
                            just_me_patterns.add(stripped)
            except Exception as e:
                print(f"Warning: Could not load just_me patterns: {e}")
        
        # Check cache first (but invalidate if filters changed)
        cache_valid = False
        if use_cache and not force_refresh and cache_manager.is_cache_valid(project_path):
            cached_metadata = cache_manager.load_metadata(project_path)
            if cached_metadata:
                # Check if filter patterns changed
                cached_exclude = cached_metadata.get('exclude_patterns_hash', '')
                cached_just_me = cached_metadata.get('just_me_patterns_hash', '')
                
                current_exclude_hash = str(hash(frozenset(exclude_patterns)))
                current_just_me_hash = str(hash(frozenset(just_me_patterns)))
                
                if cached_exclude == current_exclude_hash and cached_just_me == current_just_me_hash:
                    cache_valid = True
        
        if cache_valid:
            cached_files = cache_manager.load_parsed_files(project_path)
            cached_graph = cache_manager.load_dependency_graph(project_path)
            
            if cached_files and cached_graph:
                metadata = cache_manager.load_metadata(project_path)
                
                return jsonify({
                    'status': 'success',
                    'cached': True,
                    'file_count': len(cached_files),
                    'metadata': metadata,
                    'filters_applied': {
                        'exclude_patterns': len(exclude_patterns),
                        'just_me_patterns': len(just_me_patterns),
                        'total_files_scanned': metadata.get('total_files_scanned', 0)
                    }
                })
        
        # Fresh scan with filtering
        import time
        start_time = time.time()
        
        parsed_files = {}
        analyzer = DependencyAnalyzer(project_path, alias_config=current_app.config.get('ALIAS_CONFIG', {}))
        total_files_scanned = 0
        
        # Get the filtering functions from the text extractors
        from server.extractors.TextEXtractor import is_excluded, dir_should_keep
        
        base_folder = project_path
        
        # Scan all supported file types with enhanced technology detection
        for root, dirs, files in os.walk(project_path):
            total_files_scanned += len(files)
            
            # Apply directory filtering based on exclude patterns
            original_dirs = dirs[:]
            dirs[:] = [d for d in dirs if not is_excluded(root, d, exclude_patterns, base_folder)]
            
            # Apply just_me directory filtering
            if just_me_patterns:
                dirs[:] = [d for d in dirs if dir_should_keep(os.path.join(root, d), just_me_patterns, exclude_patterns, base_folder)]
            elif exclude_patterns:
                # If we have exclude patterns but no just_me, keep all dirs except excluded ones
                pass  # Already filtered above
            
            # Optionally skip test directories
            if not include_tests:
                dirs[:] = [d for d in dirs if d not in ['tests', 'test']]
            
            # Process files with enhanced technology detection
            for file in files:
                # Determine file type and technology stack
                file_ext = os.path.splitext(file)[1].lower()
                
                # Skip non-source files (now supporting multiple technologies)
                if file_ext not in ['.py', '.js', '.ts', '.tsx', '.jsx', '.css', '.scss', '.sass', '.less', '.html', '.vue', '.json']:
                    continue
                    
                filepath = os.path.join(root, file)
                
                # Apply file-level exclude filtering
                if is_excluded(root, file, exclude_patterns, base_folder):
                    continue
                
                # Apply just_me file filtering
                if just_me_patterns:
                    # Check if file matches any just_me pattern
                    file_matches = False
                    
                    # Get relative path for pattern matching
                    try:
                        rel_path = os.path.relpath(filepath, base_folder).replace("\\", "/")
                    except ValueError:
                        # Handle cases where filepath is on a different drive
                        rel_path = os.path.abspath(filepath).replace("\\", "/")
                    
                    for pattern in just_me_patterns:
                        pattern_norm = pattern.replace("\\", "/")
                        
                        # Exact match
                        if pattern_norm == rel_path:
                            file_matches = True
                            break
                        
                        # Substring match
                        if pattern_norm in rel_path:
                            file_matches = True
                            break
                        
                        # Filename match (backward compatibility)
                        if pattern == file:
                            file_matches = True
                            break
                    
                    if not file_matches:
                        continue
                
                # Enhanced technology detection
                technology = _detect_technology(filepath, root)
                
                # Parse file using the updated CodeParser
                try:
                    parsed = parser.parse_file(filepath)
                    if parsed:
                        parsed['technology'] = technology
                        parsed['_mtime'] = os.path.getmtime(filepath)
                        parsed_files[filepath] = parsed
                        analyzer.add_parsed_file(parsed)
                except Exception as e:
                    print(f"Warning: Could not parse {filepath}: {repr(e)}")
                    continue
        
        # Build graphs
        file_graph = analyzer.build_file_graph()
        function_graph = analyzer.build_function_graph()
        
        # Debug: Log edge counts
        print(f"DEBUG: File graph - {len(file_graph['nodes'])} nodes, {len(file_graph['edges'])} edges")
        print(f"DEBUG: Function graph - {len(function_graph['nodes'])} nodes, {len(function_graph['edges'])} edges")
        
        # Sample edges for debugging
        if file_graph['edges']:
            print(f"DEBUG: Sample file edge: {file_graph['edges'][0]}")
        if function_graph['edges']:
            print(f"DEBUG: Sample function edge: {function_graph['edges'][0]}")
        
        # Calculate stats
        total_functions = sum(len(data.get('functions', [])) for data in parsed_files.values())
        total_classes = sum(len(data.get('classes', [])) for data in parsed_files.values())
        
        scan_time = time.time() - start_time
        
        # Generate hash for filter patterns for cache invalidation
        exclude_hash = str(hash(frozenset(exclude_patterns)))
        just_me_hash = str(hash(frozenset(just_me_patterns)))
        
        # Combine both graphs for storage
        combined_graph = {
            'file_graph': file_graph,
            'function_graph': function_graph,
            'nodes': file_graph['nodes'],  # Default to file-level view
            'edges': file_graph['edges']
        }
        
        # Save to cache with filter information
        cache_manager.save_parsed_files(project_path, parsed_files)
        cache_manager.save_dependency_graph(project_path, combined_graph)
        cache_manager.save_metadata(project_path, {
            'file_count': len(parsed_files),
            'function_count': total_functions,
            'class_count': total_classes,
            'scan_time': scan_time,
            'total_files_scanned': total_files_scanned,
            'exclude_patterns_hash': exclude_hash,
            'just_me_patterns_hash': just_me_hash,
            'exclude_patterns_count': len(exclude_patterns),
            'just_me_patterns_count': len(just_me_patterns)
        })
        
        return jsonify({
            'status': 'success',
            'cached': False,
            'file_count': len(parsed_files),
            'function_count': total_functions,
            'class_count': total_classes,
            'scan_time': round(scan_time, 2),
            'filters_applied': {
                'exclude_patterns': len(exclude_patterns),
                'just_me_patterns': len(just_me_patterns),
                'total_files_scanned': total_files_scanned,
                'files_processed': len(parsed_files)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@visualizer_bp.route('/api/visualizer/graph', methods=['GET'])
def get_graph():
    """
    Get dependency graph data for visualization
    
    Query params:
    - project_path: Path to project (optional, uses config if not provided)
    - graph_type: 'file' or 'function' (default: 'file')
    
    Returns:
    {
        "nodes": [...],
        "edges": [...]
    }
    """
    try:
        project_path = request.args.get('project_path')
        graph_type = request.args.get('graph_type', 'file')
        
        if not project_path:
            config = get_config()
            project_path = config.get('TARGET_FOLDER')
        
        project_path = os.path.abspath(project_path)
        
        # Try to load from cache
        graph_data = cache_manager.load_dependency_graph(project_path)
        
        if not graph_data:
            return jsonify({
                'status': 'error',
                'message': 'No graph data found. Run scan first.'
            }), 404
        
        # Extract the requested graph type
        if graph_type == 'function' and 'function_graph' in graph_data:
            result = graph_data['function_graph']
        elif graph_type == 'file' and 'file_graph' in graph_data:
            result = graph_data['file_graph']
        else:
            # Fallback to default nodes/edges
            result = {
                'nodes': graph_data.get('nodes', []),
                'edges': graph_data.get('edges', [])
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@visualizer_bp.route('/api/visualizer/file/<path:filepath>', methods=['GET'])
def get_file_details(filepath):
    """
    Get detailed information about a specific file
    
    Returns parsed data + dependency information
    """
    try:
        project_path = request.args.get('project_path')
        
        if not project_path:
            config = get_config()
            project_path = config.get('TARGET_FOLDER')
        
        project_path = os.path.abspath(project_path)
        
        # Load parsed files
        parsed_files = cache_manager.load_parsed_files(project_path)
        
        if not parsed_files:
            return jsonify({
                'status': 'error',
                'message': 'No data found. Run scan first.'
            }), 404
        
        # Find file (filepath is relative)
        full_path = os.path.join(project_path, filepath)
        
        if full_path not in parsed_files:
            return jsonify({
                'status': 'error',
                'message': 'File not found in parsed data'
            }), 404
        
        file_data = parsed_files[full_path]
        
        # Get dependency info
        analyzer = DependencyAnalyzer(project_path)
        for fp, data in parsed_files.items():
            analyzer.add_parsed_file(data)
        
        analyzer.build_file_graph()
        dependencies = analyzer.get_file_dependencies(full_path)
        
        # Combine data
        result = {
            **file_data,
            'dependencies': dependencies
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@visualizer_bp.route('/api/visualizer/stats', methods=['GET'])
def get_stats():
    """
    Get project statistics and cache info
    """
    try:
        project_path = request.args.get('project_path')
        
        if not project_path:
            config = get_config()
            project_path = config.get('TARGET_FOLDER')
        
        project_path = os.path.abspath(project_path)
        
        # Load metadata
        metadata = cache_manager.load_metadata(project_path)
        cache_stats = cache_manager.get_cache_stats(project_path)
        
        return jsonify({
            'metadata': metadata,
            'cache': cache_stats
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@visualizer_bp.route('/api/visualizer/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear visualization cache
    
    Request body:
    {
        "project_path": "/path/to/project"  // optional, clears all if not provided
    }
    """
    try:
        data = request.get_json() or {}
        project_path = data.get('project_path')
        
        if project_path:
            project_path = os.path.abspath(project_path)
        
        cache_manager.clear_cache(project_path)
        
        return jsonify({
            'status': 'success',
            'message': 'Cache cleared'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@visualizer_bp.route('/visualizer')
def visualizer_page():
    """
    Render Code Explorer page
    """
    return render_template('CodeExplorer.html')


@visualizer_bp.route('/api/visualizer/config', methods=['GET'])
def get_visualizer_config():
    """
    Get current filtering configuration for display in visualizer
    
    Returns:
    {
        "success": true,
        "config": {
            "project_path": "/path/to/project",
            "exclude_file": "/path/to/exclude.txt",
            "just_me_file": "/path/to/just_me.txt",
            "exclude_count": 15,
            "just_me_count": 3
        }
    }
    """
    try:
        config = get_config()
        
        # Get current project path
        project_path = config.get('TARGET_FOLDER', '')
        exclude_file = config.get('EXCLUDE_FILE_PATH', '')
        just_me_file = config.get('JUST_ME_FILE_PATH', '')
        
        # Count active patterns
        exclude_count = 0
        if exclude_file and os.path.exists(exclude_file):
            try:
                with open(exclude_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped and not stripped.startswith('#'):
                            exclude_count += 1
            except Exception:
                pass
        
        just_me_count = 0
        if just_me_file and os.path.exists(just_me_file):
            try:
                with open(just_me_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped and not stripped.startswith('#'):
                            just_me_count += 1
            except Exception:
                pass
        
        return jsonify({
            'success': True,
            'config': {
                'project_path': project_path,
                'exclude_file': exclude_file,
                'just_me_file': just_me_file,
                'exclude_count': exclude_count,
                'just_me_count': just_me_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _detect_technology(filepath: str, root: str) -> str:
    """Detect technology stack from file path and content"""
    filename = os.path.basename(filepath)
    file_ext = os.path.splitext(filename)[1].lower()
    try:
        rel_path = os.path.relpath(filepath, root).replace("\\", "/")
    except ValueError:
        rel_path = os.path.abspath(filepath).replace("\\", "/")
    
    # Check for Next.js indicators
    if 'pages' in rel_path or 'app' in rel_path or filename == 'next.config.js':
        return 'nextjs'
    
    # Check for React indicators
    if filename.endswith('.jsx') or 'react' in rel_path.lower():
        return 'react'
    
    # Check for Vue.js
    if filename.endswith('.vue'):
        return 'vue'
    
    # Check for Node.js/Express
    if file_ext == '.js' and ('server' in rel_path.lower() or 'api' in rel_path.lower()):
        return 'nodejs'
    
    # Check for Express.js
    if 'express' in rel_path.lower() or filename.endswith('.server.js'):
        return 'express'
    
    # Return language as fallback
    language_map = {
        '.py': 'python',
        '.js': 'javascript', 
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.css': 'css',
        '.scss': 'css',
        '.sass': 'css',
        '.less': 'css',
        '.html': 'html',
        '.vue': 'vue',
        '.json': 'json'
    }
    return language_map.get(file_ext, 'unknown')


