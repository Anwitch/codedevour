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
import re
import esprima
from typing import Dict, List, Optional, Any


class CodeParser:
    """Parse source code files from multiple programming languages"""
    
    def __init__(self):
        self.supported_extensions = [
            '.py',           # Python
            '.js', '.jsx',   # JavaScript
            '.ts', '.tsx',   # TypeScript
            '.java',         # Java
            '.c', '.h',      # C
            '.cpp', '.hpp', '.cc', '.cxx',  # C++
            '.go',           # Go
            '.rs',           # Rust
            '.php',          # PHP
            '.rb',           # Ruby
            '.cs',           # C#
            '.swift',        # Swift
            '.kt', '.kts',   # Kotlin
        ]
    
    def is_supported(self, filepath: str) -> bool:
        """Check if file extension is supported"""
        _, ext = os.path.splitext(filepath)
        return ext in self.supported_extensions
    
    def parse_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Parse a source code file and extract structural information
        
        Args:
            filepath: Absolute path to the source file
            
        Returns:
            Dictionary containing file metadata, functions, classes, and imports
            None if parsing fails
        """
        if not self.is_supported(filepath):
            return None
        
        _, ext = os.path.splitext(filepath)
        
        # AST-based parsers (more accurate)
        if ext == '.py':
            return self._parse_python_file(filepath)
        elif ext in ['.js', '.ts', '.tsx', '.jsx']:
            return self._parse_js_ts_file(filepath)
        
        # Regex-based parsers (fallback for languages without AST libraries)
        elif ext == '.java':
            return self._parse_java_file(filepath)
        elif ext in ['.c', '.h', '.cpp', '.hpp', '.cc', '.cxx']:
            return self._parse_c_cpp_file(filepath)
        elif ext == '.go':
            return self._parse_go_file(filepath)
        elif ext == '.rs':
            return self._parse_rust_file(filepath)
        elif ext == '.php':
            return self._parse_php_file(filepath)
        elif ext == '.rb':
            return self._parse_ruby_file(filepath)
        elif ext == '.cs':
            return self._parse_csharp_file(filepath)
        elif ext == '.swift':
            return self._parse_swift_file(filepath)
        elif ext in ['.kt', '.kts']:
            return self._parse_kotlin_file(filepath)
        
        return None

    def _parse_python_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse a Python file and extract structural information"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=filepath)
            
            return {
                'filepath': filepath,
                'language': 'python',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._extract_functions(tree, source),
                'classes': self._extract_classes(tree, source),
                'imports': self._extract_imports(tree)
            }
        except Exception as e:
            print(f"Error parsing Python file {filepath}: {e}")
            return None

    def _parse_js_ts_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse a JavaScript/TypeScript file using esprima or regex fallback"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Use regex for .tsx/.jsx files, esprima for .js/.ts
            _, ext = os.path.splitext(filepath)
            
            if ext in ['.tsx', '.jsx']:
                # Regex fallback for JSX/TSX files
                functions = self._regex_extract_js_functions(source)
                classes = self._regex_extract_js_classes(source)
                imports = self._regex_extract_js_imports(source)
            else:
                # Use esprima for .js and .ts files
                try:
                    tree = esprima.parseModule(source, {'loc': True})
                except:
                    tree = esprima.parseScript(source, {'loc': True}) # Fallback
                
                functions = self._esprima_extract_functions(tree)
                classes = self._esprima_extract_classes(tree)
                imports = self._esprima_extract_imports(tree)
            
            return {
                'filepath': filepath,
                'language': 'typescript' if filepath.endswith(('.ts', '.tsx')) else 'javascript',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': functions,
                'classes': classes,
                'imports': imports
            }
        except Exception as e:
            print(f"Error parsing JS/TS file {filepath}: {e}")
            return None

    def _esprima_extract_imports(self, tree) -> List[Dict[str, Any]]:
        """Extract import statements and require calls from esprima AST"""
        imports = []

        def traverse(node):
            # Handle ES6 import statements
            if node.type == 'ImportDeclaration':
                module = node.source.value
                items = [spec.local.name for spec in node.specifiers]
                imports.append({
                    'module': module,
                    'items': items,
                    'line': node.loc.start.line
                })

            # Handle CommonJS require statements
            if node.type == 'VariableDeclarator' and node.init and node.init.type == 'CallExpression' and node.init.callee.name == 'require':
                if node.init.arguments and len(node.init.arguments) > 0:
                    module = node.init.arguments[0].value
                    
                    items = []
                    if node.id.type == 'Identifier':
                        items.append(node.id.name)
                    elif node.id.type == 'ObjectPattern':
                        for prop in node.id.properties:
                            items.append(prop.key.name)

                    imports.append({
                        'module': module,
                        'items': items,
                        'line': node.loc.start.line
                    })

            # Recursively traverse children
            for key in dir(node):
                if not key.startswith('_'):
                    child = getattr(node, key)
                    if isinstance(child, esprima.nodes.Node):
                        traverse(child)
                    elif isinstance(child, list):
                        for item in child:
                            if isinstance(item, esprima.nodes.Node):
                                traverse(item)
        
        traverse(tree)
        return imports

    def _esprima_extract_functions(self, tree) -> List[Dict[str, Any]]:
        """Extract function definitions from esprima AST using traversal"""
        functions = []
        
        def traverse(node):
            # Standard function declarations: function foo() {}
            if node.type == 'FunctionDeclaration' and node.id:
                functions.append({
                    'name': node.id.name,
                    'line_start': node.loc.start.line,
                    'line_end': node.loc.end.line,
                    'parameters': [p.name for p in node.params],
                    'calls': self._esprima_extract_calls(node.body),
                    'is_async': node.isAsync
                })

            # Arrow functions assigned to variables: const foo = () => {}
            if node.type == 'VariableDeclarator' and node.init and node.init.type == 'ArrowFunctionExpression':
                functions.append({
                    'name': node.id.name,
                    'line_start': node.loc.start.line,
                    'line_end': node.loc.end.line,
                    'parameters': [p.name for p in node.init.params],
                    'calls': self._esprima_extract_calls(node.init.body),
                    'is_async': node.init.isAsync
                })

            # Recursively traverse children
            for key in dir(node):
                if not key.startswith('_'):
                    child = getattr(node, key)
                    if isinstance(child, esprima.nodes.Node):
                        traverse(child)
                    elif isinstance(child, list):
                        for item in child:
                            if isinstance(item, esprima.nodes.Node):
                                traverse(item)
        
        traverse(tree)
        return functions

    def _esprima_extract_classes(self, tree) -> List[Dict[str, Any]]:
        """Extract class definitions from esprima AST"""
        classes = []
        
        def traverse(node):
            if node.type == 'ClassDeclaration':
                classes.append({
                    'name': node.id.name,
                    'line_start': node.loc.start.line,
                    'line_end': node.loc.end.line,
                    'methods': self._esprima_extract_methods(node.body)
                })

            # Recursively traverse children
            for key in dir(node):
                if not key.startswith('_'):
                    child = getattr(node, key)
                    if isinstance(child, esprima.nodes.Node):
                        traverse(child)
                    elif isinstance(child, list):
                        for item in child:
                            if isinstance(item, esprima.nodes.Node):
                                traverse(item)
        
        traverse(tree)
        return classes

    def _esprima_extract_methods(self, class_node) -> list:
        """Extract methods from an esprima class node"""
        methods = []
        if hasattr(class_node, 'body') and hasattr(class_node.body, 'body'):
            for node in class_node.body.body:
                if node.type == 'MethodDefinition':
                    methods.append({
                        'name': node.key.name,
                        'line_start': node.loc.start.line,
                        'line_end': node.loc.end.line,
                        'parameters': [p.name for p in node.value.params],
                        'calls': self._esprima_extract_calls(node.value.body),
                        'is_async': node.value.isAsync
                    })
        return methods

    def _esprima_extract_calls(self, node) -> List[str]:
        """Recursively extract function calls from an esprima node"""
        calls = []
        
        def traverse(node):
            if node.type == 'CallExpression':
                # Simple call: foo()
                if node.callee.type == 'Identifier':
                    calls.append(node.callee.name)
                # Member call: foo.bar()
                elif node.callee.type == 'MemberExpression' and node.callee.property.type == 'Identifier':
                    calls.append(node.callee.property.name)

            # Recursively traverse children
            for key in dir(node):
                if not key.startswith('_'):
                    child = getattr(node, key)
                    if isinstance(child, esprima.nodes.Node):
                        traverse(child)
                    elif isinstance(child, list):
                        for item in child:
                            if isinstance(item, esprima.nodes.Node):
                                traverse(item)
        
        traverse(node)
        return list(set(calls)) # Return unique calls
    
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

    # ============================================================================
    # REGEX-BASED PARSERS FOR OTHER LANGUAGES
    # ============================================================================
    
    def _regex_extract_js_imports(self, source: str) -> List[Dict[str, Any]]:
        """Extract JavaScript/TypeScript import statements using regex"""
        imports = []
        
        # Match: import React from 'react'
        # Match: import { useState, useEffect } from 'react'
        # Match: import * as utils from './utils'
        # Match: const module = require('module')
        pattern = r'^\s*import\s+(?:(\w+)|(?:\{([^}]+)\})|(?:\*\s+as\s+(\w+)))?\s*(?:,\s*\{([^}]+)\})?\s*from\s+[\'"]([^\'"]+)[\'"]'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                default_import = match.group(1)
                named_imports = match.group(2) or match.group(4)
                namespace_import = match.group(3)
                module = match.group(5)
                
                items = []
                if default_import:
                    items.append(default_import)
                if namespace_import:
                    items.append(f"* as {namespace_import}")
                if named_imports:
                    items.extend([imp.strip() for imp in named_imports.split(',')])
                
                imports.append({
                    'module': module,
                    'items': items,
                    'line': i
                })
        
        # Also match require() statements
        require_pattern = r'(?:const|let|var)\s+(?:\{([^}]+)\}|(\w+))\s*=\s*require\([\'"]([^\'"]+)[\'"]\)'
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(require_pattern, line)
            if match:
                destructured = match.group(1)
                single = match.group(2)
                module = match.group(3)
                
                items = []
                if single:
                    items.append(single)
                if destructured:
                    items.extend([imp.strip() for imp in destructured.split(',')])
                
                imports.append({
                    'module': module,
                    'items': items,
                    'line': i
                })
        
        return imports
    
    def _regex_extract_js_functions(self, source: str) -> List[Dict[str, Any]]:
        """Extract JavaScript function definitions using regex"""
        functions = []
        seen = set()  # Track unique function positions to avoid duplicates
        
        # Match: function myFunc(param1, param2) { }
        # Match: const myFunc = (param1, param2) => { }
        # Match: const myFunc = async (param1, param2) => { }
        # Match: async function myFunc(params) { }
        # Match: myMethod(params) { } (class methods)
        # Match: async myMethod(params) { } (async class methods)
        
        patterns = [
            # Standard function declarations
            (r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)', 'function'),
            # Arrow functions assigned to const/let/var
            (r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>', 'arrow'),
            # Function expressions
            (r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\(([^)]*)\)', 'expression'),
        ]
        
        # First pass: get standalone functions
        for pattern, pattern_type in patterns:
            for match in re.finditer(pattern, source):
                func_name = match.group(1)
                params = match.group(2).strip()
                line_num = source[:match.start()].count('\n') + 1
                pos_key = (func_name, line_num)
                
                if pos_key in seen:
                    continue
                seen.add(pos_key)
                
                # Parse parameters
                param_list = []
                if params:
                    for param in params.split(','):
                        param = param.strip()
                        if param:
                            # Extract parameter name (ignore type annotations, defaults)
                            param_name = param.split(':')[0].split('=')[0].strip()
                            if param_name and not param_name.startswith('{'):
                                param_list.append(param_name)
                
                # Check if async
                is_async = 'async' in source[max(0, match.start()-10):match.start()]
                
                functions.append({
                    'name': func_name,
                    'line_start': line_num,
                    'line_end': line_num,
                    'parameters': param_list,
                    'calls': [],
                    'is_async': is_async
                })
        
        # Second pass: extract class methods by finding class definitions and their bodies
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{'
        
        for class_match in re.finditer(class_pattern, source):
            class_start = class_match.end() - 1  # Position of opening brace
            
            # Find matching closing brace for this class
            brace_count = 0
            class_end = class_start
            for i in range(class_start, len(source)):
                if source[i] == '{':
                    brace_count += 1
                elif source[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break
            
            if class_end == class_start:
                continue  # No matching brace found
            
            # Extract class body
            class_body = source[class_start+1:class_end]
            
            # Within class body, find methods
            method_pattern = r'(async\s+|static\s+|private\s+|public\s+|protected\s+)*(\w+)\s*\(([^)]*)\)\s*(?::\s*[\w<>[\]|&\s]+)?\s*\{'
            
            for method_match in re.finditer(method_pattern, class_body):
                modifiers = method_match.group(1) or ''
                func_name = method_match.group(2)
                params = method_match.group(3).strip()
                
                # Calculate absolute position in source
                abs_pos = class_start + 1 + method_match.start()
                line_num = source[:abs_pos].count('\n') + 1
                pos_key = (func_name, line_num)
                
                # Skip if already added or is a control structure
                if pos_key in seen or func_name in ['if', 'for', 'while', 'switch', 'catch', 'with']:
                    continue
                
                seen.add(pos_key)
                
                # Parse parameters
                param_list = []
                if params:
                    for param in params.split(','):
                        param = param.strip()
                        if param:
                            # Extract parameter name (ignore type annotations, defaults)
                            param_name = param.split(':')[0].split('=')[0].strip()
                            if param_name and not param_name.startswith('{'):
                                param_list.append(param_name)
                
                is_async = 'async' in modifiers
                
                functions.append({
                    'name': func_name,
                    'line_start': line_num,
                    'line_end': line_num,
                    'parameters': param_list,
                    'calls': [],
                    'is_async': is_async
                })
        
        return functions
    
    def _regex_extract_js_classes(self, source: str) -> List[Dict[str, Any]]:
        """Extract JavaScript class definitions using regex"""
        classes = []
        
        # Match: class MyClass extends Component { }
        pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        
        for match in re.finditer(pattern, source):
            class_name = match.group(1)
            extends = match.group(2)
            line_num = source[:match.start()].count('\n') + 1
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'line_end': line_num,
                'extends': extends,
                'methods': []
            })
        
        return classes
    
    def _parse_java_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse Java file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return {
                'filepath': filepath,
                'language': 'java',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_java_methods(source),
                'classes': self._regex_extract_java_classes(source),
                'imports': self._regex_extract_java_imports(source)
            }
        except Exception as e:
            print(f"Error parsing Java file {filepath}: {e}")
            return None
    
    def _regex_extract_java_imports(self, source: str) -> List[Dict[str, Any]]:
        """Extract Java import statements"""
        imports = []
        # Match: import package.Class; or import static package.Class.method;
        pattern = r'^\s*import\s+(?:static\s+)?([^;]+);'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                import_path = match.group(1).strip()
                parts = import_path.split('.')
                module = '.'.join(parts[:-1]) if len(parts) > 1 else ''
                item = parts[-1] if parts else import_path
                
                imports.append({
                    'module': module,
                    'items': [item] if item != '*' else [],
                    'line': i
                })
        
        return imports
    
    def _regex_extract_java_classes(self, source: str) -> List[Dict[str, Any]]:
        """Extract Java class definitions"""
        classes = []
        # Match: public class MyClass extends Parent implements Interface {
        pattern = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            class_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'line_end': line_num,  # Approximate
                'methods': []  # Would need more complex parsing for methods
            })
        
        return classes
    
    def _regex_extract_java_methods(self, source: str) -> List[Dict[str, Any]]:
        """Extract Java method definitions"""
        methods = []
        # Match: public static void main(String[] args) {
        pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:synchronized)?\s*(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            return_type = match.group(1)
            method_name = match.group(2)
            params = match.group(3).strip()
            line_num = source[:match.start()].count('\n') + 1
            
            # Parse parameters
            param_list = []
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        parts = param.split()
                        if len(parts) >= 2:
                            param_list.append(parts[-1])  # Parameter name
            
            methods.append({
                'name': method_name,
                'line_start': line_num,
                'line_end': line_num,
                'parameters': param_list,
                'calls': [],
                'return_type': return_type
            })
        
        return methods
    
    def _parse_c_cpp_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse C/C++ file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            _, ext = os.path.splitext(filepath)
            is_cpp = ext in ['.cpp', '.hpp', '.cc', '.cxx']
            
            return {
                'filepath': filepath,
                'language': 'cpp' if is_cpp else 'c',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_c_functions(source),
                'classes': self._regex_extract_cpp_classes(source) if is_cpp else [],
                'imports': self._regex_extract_c_includes(source)
            }
        except Exception as e:
            print(f"Error parsing C/C++ file {filepath}: {e}")
            return None
    
    def _regex_extract_c_includes(self, source: str) -> List[Dict[str, Any]]:
        """Extract C/C++ #include directives"""
        includes = []
        pattern = r'^\s*#include\s+[<"]([^>"]+)[>"]'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                header = match.group(1)
                includes.append({
                    'module': header,
                    'items': [],
                    'line': i
                })
        
        return includes
    
    def _regex_extract_c_functions(self, source: str) -> List[Dict[str, Any]]:
        """Extract C/C++ function definitions"""
        functions = []
        # Match: int main(int argc, char* argv[]) {
        pattern = r'(?:static\s+)?(?:inline\s+)?(\w+(?:\s*\*)?)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        
        for match in re.finditer(pattern, source):
            return_type = match.group(1).strip()
            func_name = match.group(2)
            params = match.group(3).strip()
            line_num = source[:match.start()].count('\n') + 1
            
            # Skip common keywords that aren't functions
            if func_name in ['if', 'while', 'for', 'switch', 'catch']:
                continue
            
            param_list = []
            if params and params != 'void':
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        # Extract parameter name (last word)
                        parts = re.split(r'\s+', param)
                        if parts:
                            param_name = parts[-1].strip('*&[]')
                            param_list.append(param_name)
            
            functions.append({
                'name': func_name,
                'line_start': line_num,
                'line_end': line_num,
                'parameters': param_list,
                'calls': [],
                'return_type': return_type
            })
        
        return functions
    
    def _regex_extract_cpp_classes(self, source: str) -> List[Dict[str, Any]]:
        """Extract C++ class definitions"""
        classes = []
        pattern = r'class\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+\w+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            class_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'line_end': line_num,
                'methods': []
            })
        
        return classes
    
    def _parse_go_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse Go file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return {
                'filepath': filepath,
                'language': 'go',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_go_functions(source),
                'classes': self._regex_extract_go_structs(source),
                'imports': self._regex_extract_go_imports(source)
            }
        except Exception as e:
            print(f"Error parsing Go file {filepath}: {e}")
            return None
    
    def _regex_extract_go_imports(self, source: str) -> List[Dict[str, Any]]:
        """Extract Go import statements"""
        imports = []
        
        # Single import: import "fmt"
        single_pattern = r'^\s*import\s+"([^"]+)"'
        # Multi import block
        multi_pattern = r'import\s*\((.*?)\)'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(single_pattern, line)
            if match:
                imports.append({
                    'module': match.group(1),
                    'items': [],
                    'line': i
                })
        
        # Handle multi-line import blocks
        for match in re.finditer(multi_pattern, source, re.DOTALL):
            block = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            for line in block.split('\n'):
                line = line.strip()
                if line and line.startswith('"'):
                    module = line.strip('"')
                    imports.append({
                        'module': module,
                        'items': [],
                        'line': line_num
                    })
                    line_num += 1
        
        return imports
    
    def _regex_extract_go_functions(self, source: str) -> List[Dict[str, Any]]:
        """Extract Go function definitions"""
        functions = []
        # Match: func main() { or func (r *Receiver) Method(args) returnType {
        pattern = r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)(?:\s*[\w\*\[\]]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            func_name = match.group(1)
            params = match.group(2).strip()
            line_num = source[:match.start()].count('\n') + 1
            
            param_list = []
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        parts = param.split()
                        if parts:
                            param_list.append(parts[0])
            
            functions.append({
                'name': func_name,
                'line_start': line_num,
                'line_end': line_num,
                'parameters': param_list,
                'calls': []
            })
        
        return functions
    
    def _regex_extract_go_structs(self, source: str) -> List[Dict[str, Any]]:
        """Extract Go struct definitions (similar to classes)"""
        structs = []
        pattern = r'type\s+(\w+)\s+struct\s*\{'
        
        for match in re.finditer(pattern, source):
            struct_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            structs.append({
                'name': struct_name,
                'line_start': line_num,
                'line_end': line_num,
                'methods': []
            })
        
        return structs
    
    def _parse_rust_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse Rust file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return {
                'filepath': filepath,
                'language': 'rust',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_rust_functions(source),
                'classes': self._regex_extract_rust_structs(source),
                'imports': self._regex_extract_rust_imports(source)
            }
        except Exception as e:
            print(f"Error parsing Rust file {filepath}: {e}")
            return None
    
    def _regex_extract_rust_imports(self, source: str) -> List[Dict[str, Any]]:
        """Extract Rust use statements"""
        imports = []
        # Match: use std::io; or use std::io::{Read, Write};
        pattern = r'^\s*use\s+([^;]+);'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                import_str = match.group(1).strip()
                
                # Handle multiple imports: use std::io::{Read, Write};
                if '{' in import_str:
                    module = import_str.split('{')[0].strip(':')
                    items_str = import_str.split('{')[1].split('}')[0]
                    items = [item.strip() for item in items_str.split(',')]
                else:
                    parts = import_str.split('::')
                    module = '::'.join(parts[:-1]) if len(parts) > 1 else ''
                    items = [parts[-1]] if parts else []
                
                imports.append({
                    'module': module,
                    'items': items,
                    'line': i
                })
        
        return imports
    
    def _regex_extract_rust_functions(self, source: str) -> List[Dict[str, Any]]:
        """Extract Rust function definitions"""
        functions = []
        # Match: pub fn main() { or fn process(data: &str) -> Result<(), Error> {
        pattern = r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)(?:\s*->\s*[^{]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            func_name = match.group(1)
            params = match.group(2).strip()
            line_num = source[:match.start()].count('\n') + 1
            
            param_list = []
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        # Parameter format: name: Type
                        parts = param.split(':')
                        if parts:
                            param_list.append(parts[0].strip())
            
            functions.append({
                'name': func_name,
                'line_start': line_num,
                'line_end': line_num,
                'parameters': param_list,
                'calls': []
            })
        
        return functions
    
    def _regex_extract_rust_structs(self, source: str) -> List[Dict[str, Any]]:
        """Extract Rust struct definitions"""
        structs = []
        pattern = r'(?:pub\s+)?struct\s+(\w+)(?:<[^>]+>)?\s*\{'
        
        for match in re.finditer(pattern, source):
            struct_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            structs.append({
                'name': struct_name,
                'line_start': line_num,
                'line_end': line_num,
                'methods': []
            })
        
        return structs
    
    def _parse_php_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse PHP file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return {
                'filepath': filepath,
                'language': 'php',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_php_functions(source),
                'classes': self._regex_extract_php_classes(source),
                'imports': self._regex_extract_php_imports(source)
            }
        except Exception as e:
            print(f"Error parsing PHP file {filepath}: {e}")
            return None
    
    def _regex_extract_php_imports(self, source: str) -> List[Dict[str, Any]]:
        """Extract PHP use/require statements"""
        imports = []
        
        # Match: use App\Models\User; or require 'file.php';
        use_pattern = r'^\s*use\s+([^;]+);'
        require_pattern = r'^\s*(?:require|include)(?:_once)?\s+[\'"]([^\'\"]+)[\'"];'
        
        for i, line in enumerate(source.splitlines(), 1):
            use_match = re.match(use_pattern, line)
            if use_match:
                namespace = use_match.group(1).strip()
                parts = namespace.split('\\')
                module = '\\'.join(parts[:-1]) if len(parts) > 1 else ''
                item = parts[-1] if parts else namespace
                
                imports.append({
                    'module': module,
                    'items': [item],
                    'line': i
                })
            
            req_match = re.match(require_pattern, line)
            if req_match:
                filepath = req_match.group(1)
                imports.append({
                    'module': filepath,
                    'items': [],
                    'line': i
                })
        
        return imports
    
    def _regex_extract_php_functions(self, source: str) -> List[Dict[str, Any]]:
        """Extract PHP function definitions"""
        functions = []
        # Match: function myFunction($param1, $param2) {
        pattern = r'(?:public|private|protected)?\s*(?:static)?\s*function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*[\w\\]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            func_name = match.group(1)
            params = match.group(2).strip()
            line_num = source[:match.start()].count('\n') + 1
            
            param_list = []
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        # Extract $paramName
                        match_param = re.search(r'\$(\w+)', param)
                        if match_param:
                            param_list.append(match_param.group(1))
            
            functions.append({
                'name': func_name,
                'line_start': line_num,
                'line_end': line_num,
                'parameters': param_list,
                'calls': []
            })
        
        return functions
    
    def _regex_extract_php_classes(self, source: str) -> List[Dict[str, Any]]:
        """Extract PHP class definitions"""
        classes = []
        pattern = r'(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            class_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'line_end': line_num,
                'methods': []
            })
        
        return classes
    
    def _parse_ruby_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse Ruby file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return {
                'filepath': filepath,
                'language': 'ruby',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_ruby_methods(source),
                'classes': self._regex_extract_ruby_classes(source),
                'imports': self._regex_extract_ruby_requires(source)
            }
        except Exception as e:
            print(f"Error parsing Ruby file {filepath}: {e}")
            return None
    
    def _regex_extract_ruby_requires(self, source: str) -> List[Dict[str, Any]]:
        """Extract Ruby require statements"""
        requires = []
        pattern = r'^\s*require(?:_relative)?\s+[\'"]([^\'\"]+)[\'"]'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                module = match.group(1)
                requires.append({
                    'module': module,
                    'items': [],
                    'line': i
                })
        
        return requires
    
    def _regex_extract_ruby_methods(self, source: str) -> List[Dict[str, Any]]:
        """Extract Ruby method definitions"""
        methods = []
        # Match: def method_name(param1, param2)
        pattern = r'^\s*def\s+(?:self\.)?(\w+[?!]?)\s*(?:\(([^)]*)\))?'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                method_name = match.group(1)
                params = match.group(2) or ''
                
                param_list = []
                if params:
                    for param in params.split(','):
                        param = param.strip()
                        if param:
                            # Remove default values and type annotations
                            param = param.split('=')[0].split(':')[0].strip()
                            if param:
                                param_list.append(param)
                
                methods.append({
                    'name': method_name,
                    'line_start': i,
                    'line_end': i,
                    'parameters': param_list,
                    'calls': []
                })
        
        return methods
    
    def _regex_extract_ruby_classes(self, source: str) -> List[Dict[str, Any]]:
        """Extract Ruby class definitions"""
        classes = []
        pattern = r'^\s*class\s+(\w+)(?:\s+<\s+\w+)?'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                class_name = match.group(1)
                classes.append({
                    'name': class_name,
                    'line_start': i,
                    'line_end': i,
                    'methods': []
                })
        
        return classes
    
    def _parse_csharp_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse C# file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return {
                'filepath': filepath,
                'language': 'csharp',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_csharp_methods(source),
                'classes': self._regex_extract_csharp_classes(source),
                'imports': self._regex_extract_csharp_usings(source)
            }
        except Exception as e:
            print(f"Error parsing C# file {filepath}: {e}")
            return None
    
    def _regex_extract_csharp_usings(self, source: str) -> List[Dict[str, Any]]:
        """Extract C# using statements"""
        usings = []
        pattern = r'^\s*using\s+(?:static\s+)?([^;]+);'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                namespace = match.group(1).strip()
                usings.append({
                    'module': namespace,
                    'items': [],
                    'line': i
                })
        
        return usings
    
    def _regex_extract_csharp_methods(self, source: str) -> List[Dict[str, Any]]:
        """Extract C# method definitions"""
        methods = []
        # Match: public async Task<string> GetDataAsync(int id, string name)
        pattern = r'(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?(?:virtual\s+)?(?:override\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)'
        
        for match in re.finditer(pattern, source):
            return_type = match.group(1)
            method_name = match.group(2)
            params = match.group(3).strip()
            line_num = source[:match.start()].count('\n') + 1
            
            param_list = []
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        parts = param.split()
                        if len(parts) >= 2:
                            param_list.append(parts[-1])
            
            methods.append({
                'name': method_name,
                'line_start': line_num,
                'line_end': line_num,
                'parameters': param_list,
                'calls': [],
                'return_type': return_type
            })
        
        return methods
    
    def _regex_extract_csharp_classes(self, source: str) -> List[Dict[str, Any]]:
        """Extract C# class definitions"""
        classes = []
        pattern = r'(?:public|private|protected|internal)\s+(?:static\s+)?(?:partial\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s*:\s*[\w\s,<>]+)?\s*(?:where\s+[^{]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            class_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'line_end': line_num,
                'methods': []
            })
        
        return classes
    
    def _parse_swift_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse Swift file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return {
                'filepath': filepath,
                'language': 'swift',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_swift_functions(source),
                'classes': self._regex_extract_swift_classes(source),
                'imports': self._regex_extract_swift_imports(source)
            }
        except Exception as e:
            print(f"Error parsing Swift file {filepath}: {e}")
            return None
    
    def _regex_extract_swift_imports(self, source: str) -> List[Dict[str, Any]]:
        """Extract Swift import statements"""
        imports = []
        pattern = r'^\s*import\s+([^\s]+)'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                module = match.group(1)
                imports.append({
                    'module': module,
                    'items': [],
                    'line': i
                })
        
        return imports
    
    def _regex_extract_swift_functions(self, source: str) -> List[Dict[str, Any]]:
        """Extract Swift function definitions"""
        functions = []
        # Match: func getData(id: Int, name: String) -> Result<Data, Error> {
        pattern = r'(?:public\s+)?(?:private\s+)?(?:static\s+)?func\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*[^{]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            func_name = match.group(1)
            params = match.group(2).strip()
            line_num = source[:match.start()].count('\n') + 1
            
            param_list = []
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        # Swift params: externalName internalName: Type
                        parts = param.split(':')
                        if parts:
                            name_part = parts[0].strip().split()
                            param_name = name_part[-1] if name_part else ''
                            if param_name and param_name != '_':
                                param_list.append(param_name)
            
            functions.append({
                'name': func_name,
                'line_start': line_num,
                'line_end': line_num,
                'parameters': param_list,
                'calls': []
            })
        
        return functions
    
    def _regex_extract_swift_classes(self, source: str) -> List[Dict[str, Any]]:
        """Extract Swift class definitions"""
        classes = []
        pattern = r'(?:public\s+)?(?:private\s+)?(?:final\s+)?class\s+(\w+)(?:\s*:\s*[\w\s,]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            class_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'line_end': line_num,
                'methods': []
            })
        
        return classes
    
    def _parse_kotlin_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse Kotlin file using regex patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return {
                'filepath': filepath,
                'language': 'kotlin',
                'size': os.path.getsize(filepath),
                'lines': len(source.splitlines()),
                'functions': self._regex_extract_kotlin_functions(source),
                'classes': self._regex_extract_kotlin_classes(source),
                'imports': self._regex_extract_kotlin_imports(source)
            }
        except Exception as e:
            print(f"Error parsing Kotlin file {filepath}: {e}")
            return None
    
    def _regex_extract_kotlin_imports(self, source: str) -> List[Dict[str, Any]]:
        """Extract Kotlin import statements"""
        imports = []
        pattern = r'^\s*import\s+([^\s]+)'
        
        for i, line in enumerate(source.splitlines(), 1):
            match = re.match(pattern, line)
            if match:
                import_path = match.group(1)
                parts = import_path.split('.')
                module = '.'.join(parts[:-1]) if len(parts) > 1 else ''
                item = parts[-1] if parts else import_path
                
                imports.append({
                    'module': module,
                    'items': [item] if item != '*' else [],
                    'line': i
                })
        
        return imports
    
    def _regex_extract_kotlin_functions(self, source: str) -> List[Dict[str, Any]]:
        """Extract Kotlin function definitions"""
        functions = []
        # Match: fun getData(id: Int, name: String): Result<Data> {
        pattern = r'(?:public\s+)?(?:private\s+)?(?:suspend\s+)?fun\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*[^{]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            func_name = match.group(1)
            params = match.group(2).strip()
            line_num = source[:match.start()].count('\n') + 1
            
            param_list = []
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        # Kotlin params: name: Type
                        parts = param.split(':')
                        if parts:
                            param_list.append(parts[0].strip())
            
            functions.append({
                'name': func_name,
                'line_start': line_num,
                'line_end': line_num,
                'parameters': param_list,
                'calls': []
            })
        
        return functions
    
    def _regex_extract_kotlin_classes(self, source: str) -> List[Dict[str, Any]]:
        """Extract Kotlin class definitions"""
        classes = []
        pattern = r'(?:public\s+)?(?:private\s+)?(?:open\s+)?(?:data\s+)?class\s+(\w+)(?:\s*\([^)]*\))?(?:\s*:\s*[\w\s,<>]+)?\s*\{'
        
        for match in re.finditer(pattern, source):
            class_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'line_end': line_num,
                'methods': []
            })
        
        return classes


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
