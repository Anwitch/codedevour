"""
Dependency Analyzer - Build and Analyze Code Dependency Graphs

Creates dependency graphs showing:
- File-to-file import relationships
- Function-to-function call relationships
- Centrality metrics (which files/functions are most important)
- Circular dependency detection
"""

import os
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict, deque


class DependencyAnalyzer:
    """Analyze code dependencies and build relationship graphs"""
    
    def __init__(self, project_root: str, alias_config: Dict[str, Any] = None):
        self.project_root = os.path.abspath(project_root)
        self.alias_config = alias_config or {}
        self.parsed_files = {}
        self.file_graph = {'nodes': [], 'edges': []}
        self.function_graph = {'nodes': [], 'edges': []}
    
    def add_parsed_file(self, file_data: Dict[str, Any]):
        """Add a parsed file to the analyzer"""
        filepath = file_data['filepath']
        self.parsed_files[filepath] = file_data
    
    def build_file_graph(self) -> Dict[str, Any]:
        """
        Build file-level dependency graph
        
        Returns:
            Dictionary with 'nodes' (files) and 'edges' (imports)
        """
        nodes = []
        edges = []
        file_to_module = self._build_file_module_map()
        
        for filepath, data in self.parsed_files.items():
            # Create node for this file
            rel_path = os.path.relpath(filepath, self.project_root)
            
            node = {
                'id': rel_path,
                'type': 'file',
                'size': data['size'],
                'lines': data['lines'],
                'language': data['language'],
                'functions_count': len(data['functions']),
                'classes_count': len(data['classes']),
                'filepath': filepath
            }
            nodes.append(node)
            
            # Create edges for imports
            for imp in data['imports']:
                target_file = self._resolve_import(imp['module'], filepath, file_to_module)
                
                if target_file and target_file in self.parsed_files:
                    target_rel = os.path.relpath(target_file, self.project_root)
                    
                    edge = {
                        'source': rel_path,
                        'target': target_rel,
                        'type': 'import',
                        'module': imp['module'],
                        'items': imp['items']
                    }
                    edges.append(edge)
        
        # Calculate centrality scores
        self._calculate_centrality(nodes, edges)
        
        self.file_graph = {'nodes': nodes, 'edges': edges}
        return self.file_graph
    
    def build_function_graph(self) -> Dict[str, Any]:
        """
        Build function-level call graph
        
        Returns:
            Dictionary with 'nodes' (functions) and 'edges' (calls)
        """
        nodes = []
        edges = []
        
        # Build function lookup map
        func_map = {}  # function_name -> (filepath, func_data)
        
        for filepath, data in self.parsed_files.items():
            rel_path = os.path.relpath(filepath, self.project_root)
            
            # Module-level functions
            for func in data['functions']:
                func_id = f"{rel_path}::{func['name']}"
                func_map[func['name']] = (rel_path, func)
                
                node = {
                    'id': func_id,
                    'name': func['name'],
                    'type': 'function',
                    'file': rel_path,
                    'line_start': func['line_start'],
                    'line_end': func['line_end'],
                    'parameters': func['parameters']
                }
                nodes.append(node)
            
            # Class methods
            for cls in data['classes']:
                for method in cls['methods']:
                    func_id = f"{rel_path}::{cls['name']}.{method['name']}"
                    func_map[method['name']] = (rel_path, method)
                    
                    node = {
                        'id': func_id,
                        'name': f"{cls['name']}.{method['name']}",
                        'type': 'method',
                        'class': cls['name'],
                        'file': rel_path,
                        'line_start': method['line_start'],
                        'line_end': method['line_end'],
                        'parameters': method['parameters']
                    }
                    nodes.append(node)
        
        # Build edges based on function calls
        for filepath, data in self.parsed_files.items():
            rel_path = os.path.relpath(filepath, self.project_root)
            
            for func in data['functions']:
                source_id = f"{rel_path}::{func['name']}"
                
                for call in func['calls']:
                    if call in func_map:
                        target_file, target_func = func_map[call]
                        target_id = f"{target_file}::{target_func['name']}"
                        
                        edge = {
                            'source': source_id,
                            'target': target_id,
                            'type': 'call'
                        }
                        edges.append(edge)
        
        self.function_graph = {'nodes': nodes, 'edges': edges}
        return self.function_graph
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular import chains
        
        Returns:
            List of circular dependency chains (each chain is a list of file paths)
        """
        cycles = []
        graph = self._build_adjacency_list()
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def find_dead_code(self) -> Dict[str, List[str]]:
        """
        Find unused functions and files
        
        Returns:
            Dictionary with 'unused_functions' and 'unused_files' lists
        """
        # Build reverse lookup: who imports what
        imported_files = set()
        called_functions = set()
        
        for edge in self.file_graph['edges']:
            imported_files.add(edge['target'])
        
        for edge in self.function_graph.get('edges', []):
            called_functions.add(edge['target'])
        
        # Find files that are never imported
        all_files = {node['id'] for node in self.file_graph['nodes']}
        unused_files = all_files - imported_files
        
        # Find functions that are never called
        all_functions = {node['id'] for node in self.function_graph.get('nodes', [])}
        unused_functions = all_functions - called_functions
        
        return {
            'unused_files': list(unused_files),
            'unused_functions': list(unused_functions)
        }
    
    def get_file_dependencies(self, filepath: str) -> Dict[str, Any]:
        """
        Get all dependencies for a specific file
        
        Returns:
            Dictionary with 'imports' (files this imports) and 'imported_by' (files that import this)
        """
        rel_path = os.path.relpath(filepath, self.project_root)
        
        imports = []
        imported_by = []
        
        for edge in self.file_graph['edges']:
            if edge['source'] == rel_path:
                imports.append(edge['target'])
            if edge['target'] == rel_path:
                imported_by.append(edge['source'])
        
        return {
            'imports': imports,
            'imported_by': imported_by
        }
    
    def _build_file_module_map(self) -> Dict[str, str]:
        """Build mapping from module names to file paths"""
        module_map = {}
        
        for filepath in self.parsed_files.keys():
            # Convert file path to module name (handle both Unix and Windows paths)
            rel_path = os.path.relpath(filepath, self.project_root)
            
            # Normalize path separators
            rel_path = rel_path.replace('\\', '/')
            
            # Remove extensions for module mapping
            for ext in ['.py', '.js', '.jsx', '.ts', '.tsx']:
                if rel_path.endswith(ext):
                    rel_path = rel_path[:-len(ext)]
                    break
            
            # Convert path to module name (replace / with .)
            module_name = rel_path.replace('/', '.')
            module_map[module_name] = filepath
            
            # Also add intermediate package names
            parts = module_name.split('.')
            for i in range(1, len(parts)):
                partial_module = '.'.join(parts[:i])
                if partial_module not in module_map:
                    # Try to find __init__.py for this package
                    package_dir = os.path.join(self.project_root, *parts[:i])
                    init_file = os.path.join(package_dir, '__init__.py')
                    if os.path.exists(init_file):
                        module_map[partial_module] = init_file
        
        return module_map
    
    def _resolve_import(self, module: str, current_file: str, module_map: Dict[str, str]) -> Optional[str]:
        """Resolve import statement to actual file path"""
        # Skip external/built-in modules
        external_prefixes = [
            'os', 'sys', 'json', 're', 'ast', 'time', 'datetime', 'typing',
            'flask', 'esprima', 'pathlib', 'collections', 'hashlib',
            'psutil', 'tiktoken', 'werkzeug', 'jinja2', 'click',
            'react', 'vue', 'angular', 'axios', 'lodash', 'moment',
            '@angular', '@types', 'node:', 'fs', 'path', 'http', 'https'
        ]
        if any(module.startswith(prefix) for prefix in external_prefixes):
            return None

        # --- Resolution Strategy ---
        # 1. Handle path aliases like @/
        # 2. JavaScript/TypeScript style relative imports (./, ../)
        # 3. Python style absolute and relative imports

        # 1. Handle Path Aliases
        for alias, paths in self.alias_config.items():
            # Remove '/*' from the alias
            alias_prefix = alias.replace('/*', '')
            
            if module.startswith(alias_prefix):
                for path_template in paths:
                    # Remove '/*' from the path template
                    base_path = path_template.replace('/*', '')
                    
                    # Construct the full path
                    path_after_alias = module[len(alias_prefix):]
                    potential_path = os.path.join(self.project_root, base_path, path_after_alias.replace('/', os.sep))
                    
                    # Now, try to resolve this path with extensions
                    extensions_to_try = ['.js', '.jsx', '.ts', '.tsx', '.json']
            
            # a) Check with extensions
            for ext in extensions_to_try:
                path_with_ext = potential_path + ext
                if os.path.isfile(path_with_ext) and path_with_ext in self.parsed_files:
                    return path_with_ext
            
            # b) Check for directory index file
            for ext in extensions_to_try:
                path_with_index = os.path.join(potential_path, 'index' + ext)
                if os.path.isfile(path_with_index) and path_with_index in self.parsed_files:
                    return path_with_index

        # 2. JS/TS Relative Import Resolution
        if module.startswith('./') or module.startswith('../'):
            current_dir = os.path.dirname(current_file)
            
            # Construct the absolute path
            potential_path = os.path.abspath(os.path.join(current_dir, module))

            # Check for various extensions
            extensions_to_try = ['', '.js', '.jsx', '.ts', '.tsx', '.json']
            
            # a) Check with extensions (e.g., import './utils')
            for ext in extensions_to_try:
                path_with_ext = potential_path + ext
                if os.path.isfile(path_with_ext) and path_with_ext in self.parsed_files:
                    return path_with_ext
            
            # b) Check for directory index file (e.g., import './components')
            for ext in extensions_to_try:
                path_with_index = os.path.join(potential_path, 'index' + ext)
                if os.path.isfile(path_with_index) and path_with_index in self.parsed_files:
                    return path_with_index

        # 2. Python Style Import Resolution (and fallback for JS)
        
        # a) Direct module match (e.g., 'server.config')
        if module in module_map:
            return module_map[module]

        # b) Python relative import (e.g., 'from . import config')
        if module.startswith('.'):
            current_dir = os.path.dirname(current_file)
            rel_project_dir = os.path.relpath(current_dir, self.project_root)
            
            # Normalize to use dots as separators
            package_path = rel_project_dir.replace(os.sep, '.')
            
            # Handle leading dots for levels up
            level = 0
            for char in module:
                if char == '.':
                    level += 1
                else:
                    break
            
            # Construct the absolute module path
            if level > 0:
                package_parts = package_path.split('.')
                # Go up `level - 1` directories
                base_parts = package_parts[:-(level - 1)]
                
                # Get the rest of the module path (after the dots)
                rest_of_module = module[level:]
                if rest_of_module:
                    final_module = '.'.join(base_parts + [rest_of_module])
                else:
                    final_module = '.'.join(base_parts)
                
                if final_module in module_map:
                    return module_map[final_module]

        # c) Fallback: Check if the module string corresponds to a file path from root
        # (Handles non-relative JS imports like 'components/Button')
        potential_path_from_root = os.path.join(self.project_root, module.replace('/', os.sep))
        
        extensions_to_try = ['.js', '.jsx', '.ts', '.tsx', '.py', '.json']
        
        # Check with extensions
        for ext in extensions_to_try:
            path_with_ext = potential_path_from_root + ext
            if os.path.isfile(path_with_ext) and path_with_ext in self.parsed_files:
                return path_with_ext
        
        # Check for directory index file
        for ext in extensions_to_try:
            path_with_index = os.path.join(potential_path_from_root, 'index' + ext)
            if os.path.isfile(path_with_index) and path_with_index in self.parsed_files:
                return path_with_index

        return None
    
    def _build_adjacency_list(self) -> Dict[str, List[str]]:
        """Build adjacency list from file graph edges"""
        graph = defaultdict(list)
        
        for edge in self.file_graph['edges']:
            graph[edge['source']].append(edge['target'])
        
        return dict(graph)
    
    def _calculate_centrality(self, nodes: List[Dict], edges: List[Dict]):
        """Calculate centrality scores for nodes (importance metric)"""
        # In-degree centrality: how many files import this
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        
        for edge in edges:
            in_degree[edge['target']] += 1
            out_degree[edge['source']] += 1
        
        # Normalize and add to nodes
        max_in = max(in_degree.values()) if in_degree else 1
        max_out = max(out_degree.values()) if out_degree else 1
        
        for node in nodes:
            node_id = node['id']
            node['in_degree'] = in_degree[node_id]
            node['out_degree'] = out_degree[node_id]
            
            # Combined centrality score (0-1)
            node['centrality'] = (
                (in_degree[node_id] / max_in) * 0.7 +  # Imported by others is more important
                (out_degree[node_id] / max_out) * 0.3
            )


if __name__ == '__main__':
    # Test the analyzer
    print("DependencyAnalyzer test")
    print("Use with parsed file data from CodeParser")
