"""
Unit Tests for CodeParser

Tests Python AST parsing functionality:
- Function extraction
- Class extraction
- Import extraction
- Method extraction
- Parameter extraction
"""

import unittest
import os
import tempfile
from server.visualizer.parser import CodeParser


class TestCodeParser(unittest.TestCase):
    """Test CodeParser functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = CodeParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temp files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_temp_file(self, filename, content):
        """Helper to create temporary Python file"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_parse_simple_function(self):
        """Test parsing a simple function"""
        content = """
def hello_world():
    print("Hello, World!")
    return True
"""
        filepath = self.create_temp_file('test.py', content)
        result = self.parser.parse_file(filepath)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result['functions']), 1)
        self.assertEqual(result['functions'][0]['name'], 'hello_world')
        self.assertEqual(result['functions'][0]['parameters'], [])
    
    def test_parse_function_with_parameters(self):
        """Test parsing function with parameters"""
        content = """
def greet(name, age=25, *args, **kwargs):
    return f"Hello {name}"
"""
        filepath = self.create_temp_file('test.py', content)
        result = self.parser.parse_file(filepath)
        
        func = result['functions'][0]
        self.assertEqual(func['name'], 'greet')
        self.assertIn('name', func['parameters'])
        self.assertIn('age', func['parameters'])
        self.assertIn('*args', func['parameters'])
        self.assertIn('**kwargs', func['parameters'])
    
    def test_parse_class_with_methods(self):
        """Test parsing class with methods"""
        content = """
class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, I'm {self.name}"
    
    @staticmethod
    def static_method():
        return "Static"
"""
        filepath = self.create_temp_file('test.py', content)
        result = self.parser.parse_file(filepath)
        
        self.assertEqual(len(result['classes']), 1)
        
        cls = result['classes'][0]
        self.assertEqual(cls['name'], 'Person')
        self.assertEqual(len(cls['methods']), 3)
        
        # Check method names
        method_names = [m['name'] for m in cls['methods']]
        self.assertIn('__init__', method_names)
        self.assertIn('greet', method_names)
        self.assertIn('static_method', method_names)
        
        # Check static method detection
        static = next(m for m in cls['methods'] if m['name'] == 'static_method')
        self.assertTrue(static['is_static'])
    
    def test_parse_imports(self):
        """Test parsing import statements"""
        content = """
import os
import sys
from typing import Dict, List
from flask import Flask, Blueprint
"""
        filepath = self.create_temp_file('test.py', content)
        result = self.parser.parse_file(filepath)
        
        self.assertEqual(len(result['imports']), 4)
        
        # Check import modules
        modules = [imp['module'] for imp in result['imports']]
        self.assertIn('os', modules)
        self.assertIn('sys', modules)
        self.assertIn('typing', modules)
        self.assertIn('flask', modules)
        
        # Check imported items
        typing_import = next(imp for imp in result['imports'] if imp['module'] == 'typing')
        self.assertIn('Dict', typing_import['items'])
        self.assertIn('List', typing_import['items'])
    
    def test_parse_function_calls(self):
        """Test extracting function calls"""
        content = """
def main():
    setup()
    process_data()
    cleanup()
    return True
"""
        filepath = self.create_temp_file('test.py', content)
        result = self.parser.parse_file(filepath)
        
        func = result['functions'][0]
        self.assertIn('setup', func['calls'])
        self.assertIn('process_data', func['calls'])
        self.assertIn('cleanup', func['calls'])
    
    def test_parse_async_function(self):
        """Test parsing async function"""
        content = """
async def fetch_data():
    await some_async_call()
    return data
"""
        filepath = self.create_temp_file('test.py', content)
        result = self.parser.parse_file(filepath)
        
        func = result['functions'][0]
        self.assertEqual(func['name'], 'fetch_data')
        self.assertTrue(func['is_async'])
    
    def test_parse_decorated_function(self):
        """Test parsing function with decorators"""
        content = """
@app.route('/api/test')
@login_required
def api_test():
    return "OK"
"""
        filepath = self.create_temp_file('test.py', content)
        result = self.parser.parse_file(filepath)
        
        func = result['functions'][0]
        self.assertIn('login_required', func['decorators'])
    
    def test_unsupported_file(self):
        """Test handling unsupported file type"""
        filepath = os.path.join(self.temp_dir, 'test.txt')
        with open(filepath, 'w') as f:
            f.write("Not a Python file")
        
        result = self.parser.parse_file(filepath)
        self.assertIsNone(result)
    
    def test_invalid_syntax(self):
        """Test handling file with syntax errors"""
        content = """
def broken(
    # Missing closing parenthesis and body
"""
        filepath = self.create_temp_file('test.py', content)
        result = self.parser.parse_file(filepath)
        
        # Should return None on parse error
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
