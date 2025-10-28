"""
Cache Manager - File-based Caching System for Parsed Data

Manages cache for:
- Parsed file data
- Dependency graphs
- Function indexes
- Metadata and timestamps
"""

import os
import json
import hashlib
import time
from typing import Dict, Any, Optional
from pathlib import Path


class CacheManager:
    """Manage file-based cache for visualization data"""
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files (default: server/visualizer/cache)
        """
        if cache_dir is None:
            # Default to visualizer/cache directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cache_dir = os.path.join(current_dir, 'cache')
        
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Create .gitignore to exclude cache files
        gitignore_path = os.path.join(self.cache_dir, '.gitignore')
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w') as f:
                f.write("# Ignore all cache files\n")
                f.write("*\n")
                f.write("!.gitignore\n")
    
    def _get_project_hash(self, project_path: str) -> str:
        """Generate a hash for the project path"""
        return hashlib.md5(project_path.encode()).hexdigest()[:12]
    
    def _get_project_cache_dir(self, project_path: str) -> str:
        """Get cache directory for a specific project"""
        project_hash = self._get_project_hash(project_path)
        cache_path = os.path.join(self.cache_dir, f"project_{project_hash}")
        os.makedirs(cache_path, exist_ok=True)
        return cache_path
    
    def _get_cache_file_path(self, project_path: str, cache_type: str) -> str:
        """Get path to a specific cache file"""
        project_dir = self._get_project_cache_dir(project_path)
        return os.path.join(project_dir, f"{cache_type}.json")
    
    def save_parsed_files(self, project_path: str, parsed_data: Dict[str, Any]):
        """
        Save parsed files data to cache
        
        Args:
            project_path: Absolute path to the project
            parsed_data: Dictionary of filepath -> parsed file data
        """
        cache_file = self._get_cache_file_path(project_path, 'files')
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2)
    
    def load_parsed_files(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Load parsed files data from cache
        
        Args:
            project_path: Absolute path to the project
            
        Returns:
            Dictionary of parsed file data or None if cache miss
        """
        cache_file = self._get_cache_file_path(project_path, 'files')
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
            return None
    
    def save_dependency_graph(self, project_path: str, graph_data: Dict[str, Any]):
        """Save dependency graph to cache"""
        cache_file = self._get_cache_file_path(project_path, 'dependencies')
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2)
    
    def load_dependency_graph(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Load dependency graph from cache"""
        cache_file = self._get_cache_file_path(project_path, 'dependencies')
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading dependency cache: {e}")
            return None
    
    def save_metadata(self, project_path: str, metadata: Dict[str, Any]):
        """
        Save cache metadata
        
        Metadata includes:
        - Last scan timestamp
        - File count
        - Cache version
        - Project configuration
        """
        cache_file = self._get_cache_file_path(project_path, 'metadata')
        
        # Add timestamp if not present
        if 'last_scan' not in metadata:
            metadata['last_scan'] = time.time()
        
        if 'cache_version' not in metadata:
            metadata['cache_version'] = '1.0'
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def load_metadata(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Load cache metadata"""
        cache_file = self._get_cache_file_path(project_path, 'metadata')
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return None
    
    def is_cache_valid(self, project_path: str, max_age_hours: int = 24) -> bool:
        """
        Check if cache is still valid
        
        Args:
            project_path: Absolute path to the project
            max_age_hours: Maximum age of cache in hours
            
        Returns:
            True if cache is valid, False otherwise
        """
        metadata = self.load_metadata(project_path)
        
        if not metadata:
            return False
        
        last_scan = metadata.get('last_scan', 0)
        current_time = time.time()
        age_hours = (current_time - last_scan) / 3600
        
        return age_hours < max_age_hours
    
    def should_invalidate_file(self, filepath: str, cached_data: Dict[str, Any]) -> bool:
        """
        Check if a specific file's cache should be invalidated
        
        Args:
            filepath: Absolute path to the file
            cached_data: Cached data for this file
            
        Returns:
            True if cache should be invalidated
        """
        if not os.path.exists(filepath):
            return True
        
        # Check if file modification time changed
        current_mtime = os.path.getmtime(filepath)
        cached_mtime = cached_data.get('_mtime', 0)
        
        if current_mtime > cached_mtime:
            return True
        
        # Check if file size changed
        current_size = os.path.getsize(filepath)
        cached_size = cached_data.get('size', 0)
        
        if current_size != cached_size:
            return True
        
        return False
    
    def clear_cache(self, project_path: str = None):
        """
        Clear cache for a specific project or all projects
        
        Args:
            project_path: Path to project (None to clear all)
        """
        if project_path:
            # Clear specific project cache
            project_dir = self._get_project_cache_dir(project_path)
            if os.path.exists(project_dir):
                import shutil
                shutil.rmtree(project_dir)
                print(f"Cache cleared for project: {project_path}")
        else:
            # Clear all cache
            if os.path.exists(self.cache_dir):
                for item in os.listdir(self.cache_dir):
                    if item.startswith('project_'):
                        item_path = os.path.join(self.cache_dir, item)
                        import shutil
                        shutil.rmtree(item_path)
                print("All cache cleared")
    
    def get_cache_stats(self, project_path: str = None) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Args:
            project_path: Path to project (None for all projects)
            
        Returns:
            Dictionary with cache statistics
        """
        if project_path:
            # Stats for specific project
            project_dir = self._get_project_cache_dir(project_path)
            
            if not os.path.exists(project_dir):
                return {'exists': False}
            
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    total_size += os.path.getsize(filepath)
                    file_count += 1
            
            metadata = self.load_metadata(project_path)
            
            return {
                'exists': True,
                'file_count': file_count,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'metadata': metadata
            }
        else:
            # Stats for all projects
            total_projects = 0
            total_size = 0
            
            if os.path.exists(self.cache_dir):
                for item in os.listdir(self.cache_dir):
                    if item.startswith('project_'):
                        total_projects += 1
                        project_path = os.path.join(self.cache_dir, item)
                        
                        for root, dirs, files in os.walk(project_path):
                            for file in files:
                                filepath = os.path.join(root, file)
                                total_size += os.path.getsize(filepath)
            
            return {
                'total_projects': total_projects,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }


if __name__ == '__main__':
    # Test cache manager
    cache = CacheManager()
    
    test_project = r"C:\Users\Test\MyProject"
    
    # Test save/load
    test_data = {
        'file1.py': {'name': 'file1', 'functions': []},
        'file2.py': {'name': 'file2', 'functions': []}
    }
    
    cache.save_parsed_files(test_project, test_data)
    loaded = cache.load_parsed_files(test_project)
    
    print("Cache test:")
    print(f"Saved: {len(test_data)} files")
    print(f"Loaded: {len(loaded)} files" if loaded else "Load failed")
    
    # Get stats
    stats = cache.get_cache_stats(test_project)
    print(f"\nCache stats: {stats}")
