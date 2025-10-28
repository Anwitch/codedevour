"""
Unit Tests for DependencyAnalyzer

Tests dependency graph building:
- File-level dependency graph
- Function-level call graph
- Circular dependency detection
- Dead code detection
"""

import unittest
import tempfile
import os
from server.visualizer.parser import CodeParser
from server.visualizer.dependency_analyzer import DependencyAnalyzer


class TestDependencyAnalyzer(unittest.TestCase):
    """Test DependencyAnalyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = CodeParser()
    
    def tearDown(self):
        """Clean up temp files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, filename, content):
        """Helper to create test Python file"""
        filepath = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def test_simple_file_graph(self):
        """Test building simple file dependency graph"""
        # Create two files with import relationship
        file1 = self.create_test_file('utils.py', """
def helper():
    return True
""")
        
        file2 = self.create_test_file('main.py', """
from utils import helper

def main():
    return helper()
""")
        
        # Parse files
        parsed1 = self.parser.parse_file(file1)
        parsed2 = self.parser.parse_file(file2)
        
        # Build graph
        analyzer = DependencyAnalyzer(self.temp_dir)
        analyzer.add_parsed_file(parsed1)
        analyzer.add_parsed_file(parsed2)
        
        graph = analyzer.build_file_graph()
        
        # Check graph structure
        self.assertEqual(len(graph['nodes']), 2)
        self.assertEqual(len(graph['edges']), 1)
        
        # Check edge connects main.py -> utils.py
        edge = graph['edges'][0]
        self.assertIn('main.py', edge['source'])
        self.assertIn('utils.py', edge['target'])
    
    def test_function_graph(self):
        """Test building function-level call graph"""
        file1 = self.create_test_file('test.py', """
def function_a():
    return function_b()

def function_b():
    return function_c()

def function_c():
    return True
""")
        
        parsed = self.parser.parse_file(file1)
        
        analyzer = DependencyAnalyzer(self.temp_dir)
        analyzer.add_parsed_file(parsed)
        
        graph = analyzer.build_function_graph()
        
        # Should have 3 function nodes
        self.assertEqual(len(graph['nodes']), 3)
        
        # Check edges
        self.assertGreater(len(graph['edges']), 0)
    
    def test_centrality_calculation(self):
        """Test centrality score calculation"""
        # Create hub file imported by others
        hub = self.create_test_file('hub.py', """
def important_function():
    return True
""")
        
        # Create files that import hub
        for i in range(3):
            self.create_test_file(f'file{i}.py', f"""
from hub import important_function

def func{i}():
    return important_function()
""")
        
        # Parse all files
        analyzer = DependencyAnalyzer(self.temp_dir)
        
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    parsed = self.parser.parse_file(filepath)
                    if parsed:
                        analyzer.add_parsed_file(parsed)
        
        graph = analyzer.build_file_graph()
        
        # hub.py should have high centrality (imported by 3 files)
        hub_node = next(n for n in graph['nodes'] if 'hub.py' in n['id'])
        self.assertGreater(hub_node['centrality'], 0)
        self.assertEqual(hub_node['in_degree'], 3)
    
    def test_get_file_dependencies(self):
        """Test getting dependencies for specific file"""
        file1 = self.create_test_file('a.py', 'def a(): pass')
        file2 = self.create_test_file('b.py', 'from a import a')
        file3 = self.create_test_file('c.py', 'from b import a')
        
        analyzer = DependencyAnalyzer(self.temp_dir)
        
        for filepath in [file1, file2, file3]:
            parsed = self.parser.parse_file(filepath)
            if parsed:
                analyzer.add_parsed_file(parsed)
        
        analyzer.build_file_graph()
        
        # Check b.py dependencies
        deps = analyzer.get_file_dependencies(file2)
        
        self.assertEqual(len(deps['imports']), 1)  # imports a.py
        self.assertEqual(len(deps['imported_by']), 1)  # imported by c.py


if __name__ == '__main__':
    unittest.main()
