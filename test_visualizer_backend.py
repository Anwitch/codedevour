"""
Quick Test Script for Visualizer Backend

Tests all components in isolation:
- CodeParser
- DependencyAnalyzer  
- CacheManager
- Integration test
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.visualizer import CodeParser, DependencyAnalyzer, CacheManager

def test_parser():
    """Test CodeParser with real files"""
    print("=" * 60)
    print("Testing CodeParser...")
    print("=" * 60)
    
    parser = CodeParser()
    
    # Test with this project's app.py
    test_file = 'server/app.py'
    
    if os.path.exists(test_file):
        result = parser.parse_file(test_file)
        
        if result:
            print(f"✅ Successfully parsed: {test_file}")
            print(f"   Language: {result['language']}")
            print(f"   Lines: {result['lines']}")
            print(f"   Functions: {len(result['functions'])}")
            print(f"   Classes: {len(result['classes'])}")
            print(f"   Imports: {len(result['imports'])}")
            
            if result['functions']:
                print(f"\n   Top functions:")
                for func in result['functions'][:3]:
                    print(f"   - {func['name']}({', '.join(func['parameters'])})")
        else:
            print(f"❌ Failed to parse {test_file}")
    else:
        print(f"❌ Test file not found: {test_file}")
    
    print()


def test_analyzer():
    """Test DependencyAnalyzer with multiple files"""
    print("=" * 60)
    print("Testing DependencyAnalyzer...")
    print("=" * 60)
    
    parser = CodeParser()
    analyzer = DependencyAnalyzer(os.getcwd())
    
    # Parse multiple files from server directory
    test_files = [
        'server/app.py',
        'server/config.py',
    ]
    
    parsed_count = 0
    
    for filepath in test_files:
        if os.path.exists(filepath):
            result = parser.parse_file(filepath)
            if result:
                analyzer.add_parsed_file(result)
                parsed_count += 1
    
    if parsed_count > 0:
        print(f"✅ Parsed {parsed_count} files")
        
        # Build file graph
        file_graph = analyzer.build_file_graph()
        print(f"   File graph: {len(file_graph['nodes'])} nodes, {len(file_graph['edges'])} edges")
        
        # Build function graph
        function_graph = analyzer.build_function_graph()
        print(f"   Function graph: {len(function_graph['nodes'])} nodes, {len(function_graph['edges'])} edges")
        
        # Show some nodes
        if file_graph['nodes']:
            print(f"\n   Sample nodes:")
            for node in file_graph['nodes'][:3]:
                print(f"   - {node['id']} (centrality: {node['centrality']:.2f})")
    else:
        print(f"❌ No files parsed")
    
    print()


def test_cache():
    """Test CacheManager"""
    print("=" * 60)
    print("Testing CacheManager...")
    print("=" * 60)
    
    cache = CacheManager()
    
    test_project = os.getcwd()
    test_data = {
        'test_file.py': {
            'filepath': 'test_file.py',
            'language': 'python',
            'size': 1234,
            'lines': 50,
            'functions': [],
            'classes': [],
            'imports': []
        }
    }
    
    # Save
    cache.save_parsed_files(test_project, test_data)
    print(f"✅ Saved test data to cache")
    
    # Load
    loaded = cache.load_parsed_files(test_project)
    
    if loaded and 'test_file.py' in loaded:
        print(f"✅ Successfully loaded data from cache")
        print(f"   Files in cache: {len(loaded)}")
    else:
        print(f"❌ Failed to load from cache")
    
    # Check validity
    is_valid = cache.is_cache_valid(test_project)
    print(f"   Cache valid: {is_valid}")
    
    # Get stats
    stats = cache.get_cache_stats(test_project)
    print(f"   Cache size: {stats.get('total_size_mb', 0)} MB")
    
    print()


def test_integration():
    """Integration test: Full workflow"""
    print("=" * 60)
    print("Testing Integration (Full Workflow)...")
    print("=" * 60)
    
    project_path = os.getcwd()
    
    # 1. Parse files
    parser = CodeParser()
    analyzer = DependencyAnalyzer(project_path)
    cache = CacheManager()
    
    print("Step 1: Scanning server/ directory...")
    
    file_count = 0
    for root, dirs, files in os.walk('server'):
        # Skip cache and __pycache__
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'cache']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                result = parser.parse_file(filepath)
                
                if result:
                    analyzer.add_parsed_file(result)
                    file_count += 1
    
    print(f"✅ Scanned {file_count} Python files")
    
    # 2. Build graph
    print("\nStep 2: Building dependency graph...")
    file_graph = analyzer.build_file_graph()
    
    print(f"✅ Graph built:")
    print(f"   Nodes: {len(file_graph['nodes'])}")
    print(f"   Edges: {len(file_graph['edges'])}")
    
    # 3. Find most central files
    if file_graph['nodes']:
        print("\nStep 3: Finding most important files (by centrality)...")
        sorted_nodes = sorted(file_graph['nodes'], key=lambda n: n['centrality'], reverse=True)
        
        print(f"✅ Top 5 most central files:")
        for i, node in enumerate(sorted_nodes[:5], 1):
            print(f"   {i}. {node['id']}")
            print(f"      Centrality: {node['centrality']:.3f}")
            print(f"      Imported by: {node['in_degree']} files")
            print(f"      Imports: {node['out_degree']} files")
    
    # 4. Save to cache
    print("\nStep 4: Saving to cache...")
    cache.save_dependency_graph(project_path, file_graph)
    cache.save_metadata(project_path, {
        'file_count': len(file_graph['nodes']),
        'test': 'integration_test'
    })
    print(f"✅ Data cached successfully")
    
    print()


if __name__ == '__main__':
    print("\n" + "🔍" * 30)
    print("Code Explorer Backend Test Suite")
    print("🔍" * 30 + "\n")
    
    try:
        test_parser()
        test_analyzer()
        test_cache()
        test_integration()
        
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
