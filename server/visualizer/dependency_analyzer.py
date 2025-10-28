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
    
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
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
            # Convert file path to module name
            rel_path = os.path.relpath(filepath, self.project_root)
            module_name = rel_path.replace(os.sep, '.').replace('.py', '')
            module_map[module_name] = filepath
        
        return module_map
    
    def _resolve_import(self, module: str, current_file: str, module_map: Dict[str, str]) -> Optional[str]:
        """Resolve import statement to actual file path"""
        # Try direct module name
        if module in module_map:
            return module_map[module]
        
        # Try relative imports
        current_dir = os.path.dirname(current_file)
        
        # Handle relative imports (. and ..)
        if module.startswith('.'):
            parts = module.split('.')
            level = len(parts) - len([p for p in parts if p])
            
            # Go up 'level' directories
            target_dir = current_dir
            for _ in range(level - 1):
                target_dir = os.path.dirname(target_dir)
            
            # Add remaining path
            remaining = '.'.join([p for p in parts if p])
            if remaining:
                target_path = os.path.join(target_dir, remaining.replace('.', os.sep) + '.py')
            else:
                target_path = os.path.join(target_dir, '__init__.py')
            
            if os.path.exists(target_path):
                return os.path.abspath(target_path)
        
        # Try as submodule of current package
        current_package = os.path.dirname(current_file)
        potential_path = os.path.join(current_package, module.replace('.', os.sep) + '.py')
        
        if os.path.exists(potential_path):
            return os.path.abspath(potential_path)
        
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
