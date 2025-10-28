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
from flask import Blueprint, request, jsonify, render_template
from server.config import load_config
from server.visualizer import CodeParser, DependencyAnalyzer, CacheManager

visualizer_bp = Blueprint('visualizer', __name__)

# Initialize components
parser = CodeParser()
cache_manager = CacheManager()


@visualizer_bp.route('/api/visualizer/scan', methods=['POST'])
def scan_project():
    """
    Scan project and generate visualization data
    
    Request body:
    {
        "project_path": "/path/to/project",
        "use_cache": true,
        "include_tests": false
    }
    
    Returns:
    {
        "status": "success",
        "file_count": 42,
        "function_count": 156,
        "cached": false,
        "scan_time": 2.34
    }
    """
    try:
        data = request.get_json()
        project_path = data.get('project_path')
        use_cache = data.get('use_cache', True)
        include_tests = data.get('include_tests', False)
        
        if not project_path:
            # Use config target folder
            config = load_config()
            project_path = config.get('TARGET_FOLDER')
        
        if not project_path or not os.path.exists(project_path):
            return jsonify({
                'status': 'error',
                'message': 'Invalid project path'
            }), 400
        
        project_path = os.path.abspath(project_path)
        
        # Check cache first
        if use_cache and cache_manager.is_cache_valid(project_path):
            cached_files = cache_manager.load_parsed_files(project_path)
            cached_graph = cache_manager.load_dependency_graph(project_path)
            
            if cached_files and cached_graph:
                metadata = cache_manager.load_metadata(project_path)
                
                return jsonify({
                    'status': 'success',
                    'cached': True,
                    'file_count': len(cached_files),
                    'metadata': metadata
                })
        
        # Fresh scan
        import time
        start_time = time.time()
        
        parsed_files = {}
        analyzer = DependencyAnalyzer(project_path)
        
        # Scan all Python files
        for root, dirs, files in os.walk(project_path):
            # Skip common excluded directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
            
            # Optionally skip tests
            if not include_tests:
                dirs[:] = [d for d in dirs if d not in ['tests', 'test']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    # Parse file
                    parsed = parser.parse_file(filepath)
                    
                    if parsed:
                        # Add modification time for cache invalidation
                        parsed['_mtime'] = os.path.getmtime(filepath)
                        
                        parsed_files[filepath] = parsed
                        analyzer.add_parsed_file(parsed)
        
        # Build graphs
        file_graph = analyzer.build_file_graph()
        function_graph = analyzer.build_function_graph()
        
        # Calculate stats
        total_functions = sum(len(data['functions']) for data in parsed_files.values())
        total_classes = sum(len(data['classes']) for data in parsed_files.values())
        
        scan_time = time.time() - start_time
        
        # Save to cache
        cache_manager.save_parsed_files(project_path, parsed_files)
        cache_manager.save_dependency_graph(project_path, file_graph)
        cache_manager.save_metadata(project_path, {
            'file_count': len(parsed_files),
            'function_count': total_functions,
            'class_count': total_classes,
            'scan_time': scan_time
        })
        
        return jsonify({
            'status': 'success',
            'cached': False,
            'file_count': len(parsed_files),
            'function_count': total_functions,
            'class_count': total_classes,
            'scan_time': round(scan_time, 2)
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
            config = load_config()
            project_path = config.get('TARGET_FOLDER')
        
        project_path = os.path.abspath(project_path)
        
        # Try to load from cache
        graph_data = cache_manager.load_dependency_graph(project_path)
        
        if not graph_data:
            return jsonify({
                'status': 'error',
                'message': 'No graph data found. Run scan first.'
            }), 404
        
        return jsonify(graph_data)
        
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
            config = load_config()
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
            config = load_config()
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
