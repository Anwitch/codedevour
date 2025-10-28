"""
Code Parser - Python AST Parser for Code Visualization

Extracts structural information from Python files:
- Functions and methods
- Classes
- Import statements
- Function calls
- Line numbers and parameters
"""

import ast
import os
from typing import Dict, List, Optional, Any


class CodeParser:
    """Parse Python source code files using AST"""
    
    def __init__(self):
        self.supported_extensions = ['.py']
    
    def is_supported(self, filepath: str) -> bool:
        """Check if file extension is supported"""
        _, ext = os.path.splitext(filepath)
        return ext in self.supported_extensions
    
    def parse_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Parse a Python file and extract structural information
        
        Args:
            filepath: Absolute path to the Python file
            
        Returns:
            Dictionary containing file metadata, functions, classes, and imports
            None if parsing fails
        """
        if not self.is_supported(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Parse AST
            tree = ast.parse(source, filename=filepath)
            
            # Extract information
            result = {
                'filepath': filepath,
                'language': 'python',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._extract_functions(tree, source),
                'classes': self._extract_classes(tree, source),
                'imports': self._extract_imports(tree)
            }
            
            return result
            
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None
    
    def _extract_functions(self, tree: ast.AST, source: str) -> List[Dict[str, Any]]:
        """Extract all function definitions from AST"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip methods inside classes (they'll be in _extract_classes)
                if self._is_method(node, tree):
                    continue
                
                func_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno or node.lineno,
                    'parameters': self._extract_parameters(node),
                    'calls': self._extract_function_calls(node),
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                }
                
                functions.append(func_info)
        
        return functions
    
    def _extract_classes(self, tree: ast.AST, source: str) -> List[Dict[str, Any]]:
        """Extract all class definitions from AST"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno or node.lineno,
                    'bases': [self._get_name(base) for base in node.bases],
                    'methods': self._extract_methods(node),
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
                }
                
                classes.append(class_info)
        
        return classes
    
    def _extract_methods(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract methods from a class definition"""
        methods = []
        
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno or node.lineno,
                    'parameters': self._extract_parameters(node),
                    'calls': self._extract_function_calls(node),
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'is_static': any(self._get_decorator_name(d) == 'staticmethod' for d in node.decorator_list),
                    'is_class_method': any(self._get_decorator_name(d) == 'classmethod' for d in node.decorator_list)
                }
                
                methods.append(method_info)
        
        return methods
    
    def _extract_parameters(self, func_node: ast.FunctionDef) -> List[str]:
        """Extract parameter names from function definition"""
        params = []
        
        # Regular args
        for arg in func_node.args.args:
            params.append(arg.arg)
        
        # *args
        if func_node.args.vararg:
            params.append(f"*{func_node.args.vararg.arg}")
        
        # **kwargs
        if func_node.args.kwarg:
            params.append(f"**{func_node.args.kwarg.arg}")
        
        return params
    
    def _extract_function_calls(self, node: ast.AST) -> List[str]:
        """Extract all function calls within a function/method"""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_name = self._get_call_name(child.func)
                if call_name:
                    calls.append(call_name)
        
        return list(set(calls))  # Remove duplicates
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all import statements"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'module': alias.name,
                        'alias': alias.asname,
                        'items': [],
                        'line': node.lineno
                    })
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                items = [alias.name for alias in node.names]
                
                imports.append({
                    'module': module,
                    'alias': None,
                    'items': items,
                    'line': node.lineno
                })
        
        return imports
    
    def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a method inside a class"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func_node in node.body:
                    return True
        return False
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name as string"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return self._get_name(decorator.func)
        return str(decorator)
    
    def _get_call_name(self, node: ast.AST) -> Optional[str]:
        """Get function call name"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from various AST node types"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)


if __name__ == '__main__':
    # Test the parser
    parser = CodeParser()
    
    # Test with this file itself
    result = parser.parse_file(__file__)
    
    if result:
        print(f"File: {result['filepath']}")
        print(f"Language: {result['language']}")
        print(f"Size: {result['size']} bytes")
        print(f"Lines: {result['lines']}")
        print(f"\nFunctions: {len(result['functions'])}")
        for func in result['functions'][:3]:
            print(f"  - {func['name']}({', '.join(func['parameters'])})")
        
        print(f"\nClasses: {len(result['classes'])}")
        for cls in result['classes']:
            print(f"  - {cls['name']} ({len(cls['methods'])} methods)")
        
        print(f"\nImports: {len(result['imports'])}")
        for imp in result['imports'][:5]:
            print(f"  - from {imp['module']} import {', '.join(imp['items']) if imp['items'] else '*'}")
