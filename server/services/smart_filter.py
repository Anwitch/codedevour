"""
Smart File Filtering untuk Large Projects
Menentukan prioritas file dan optimasi processing berdasarkan ukuran project
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple

from server.services.memory_manager import memory_monitor


class SmartFileFilter:
    """Smart file filtering dan prioritization system"""
    
    def __init__(self):
        # File type priorities (higher number = higher priority)
        self.file_priorities = {
            # Source code files - highest priority
            ".py": 10, ".js": 10, ".ts": 10, ".tsx": 10, ".jsx": 10,
            ".java": 9, ".kt": 9, ".go": 9, ".rs": 9, ".cpp": 9,
            ".c": 8, ".h": 8, ".hpp": 8, ".cs": 8,
            
            # Configuration files
            ".json": 8, ".yaml": 8, ".yml": 8, ".toml": 8, ".ini": 8,
            ".cfg": 8, ".conf": 8, ".config": 8,
            
            # Documentation
            ".md": 7, ".txt": 6, ".rst": 6,
            
            # Web files
            ".html": 7, ".css": 6, ".scss": 6, ".vue": 9,
            
            # Scripts
            ".sh": 7, ".bat": 7, ".ps1": 7,
            
            # Database
            ".sql": 7,
            
            # Less important files
            ".xml": 5, ".png": 1, ".jpg": 1, ".jpeg": 1, ".gif": 1,
            ".ico": 1, ".svg": 2, ".pdf": 2, ".zip": 1, ".tar": 1,
            ".gz": 1, ".log": 3, ".tmp": 1, ".cache": 1
        }
        
        # Large project thresholds
        self.thresholds = {
            "small": 100,       # < 100 files
            "medium": 1000,     # 100-1000 files  
            "large": 10000,     # 1000-10000 files
            "xlarge": 100000    # > 10000 files
        }
    
    def analyze_project_size(self, folder_path: str) -> Dict:
        """Analyze project size and characteristics"""
        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "file_types": {},
            "large_files": 0,
            "project_size_category": "unknown",
            "recommended_settings": {}
        }
        
        total_size = 0
        file_type_counts = {}
        large_files = 0
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    try:
                        # Get file stats
                        stat = os.stat(file_path)
                        file_size = stat.st_size
                        total_size += file_size
                        
                        # Count file types
                        ext = os.path.splitext(filename)[1].lower()
                        file_type_counts[ext] = file_type_counts.get(ext, 0) + 1
                        
                        # Count large files (>10MB)
                        if file_size > 10 * 1024 * 1024:
                            large_files += 1
                        
                        stats["total_files"] += 1
                        
                    except (OSError, IOError):
                        continue
            
            stats["total_size_mb"] = total_size / (1024 * 1024)
            stats["file_types"] = file_type_counts
            stats["large_files"] = large_files
            
            # Determine project size category
            if stats["total_files"] < self.thresholds["small"]:
                stats["project_size_category"] = "small"
            elif stats["total_files"] < self.thresholds["medium"]:
                stats["project_size_category"] = "medium"
            elif stats["total_files"] < self.thresholds["large"]:
                stats["project_size_category"] = "large"
            else:
                stats["project_size_category"] = "xlarge"
            
            # Get recommendations
            stats["recommended_settings"] = self.get_recommended_settings(stats)
            
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    def get_recommended_settings(self, project_stats: Dict) -> Dict:
        """Get processing recommendations berdasarkan project analysis"""
        settings = {
            "use_async": False,
            "chunk_size": 8192,
            "memory_threshold": 80,
            "batch_size": 50,
            "enable_progress_tracking": True,
            "skip_binary_files": True,
            "max_file_size_mb": 10
        }
        
        total_files = project_stats.get("total_files", 0)
        total_size_mb = project_stats.get("total_size_mb", 0)
        large_files = project_stats.get("large_files", 0)
        category = project_stats.get("project_size_category", "small")
        
        # Async processing untuk projects besar
        if total_files > 1000 or total_size_mb > 500:
            settings["use_async"] = True
        
        # Optimize chunk size based on project size
        if total_files > 10000:
            settings["chunk_size"] = 16384  # Larger chunks for very large projects
        elif total_files > 5000:
            settings["chunk_size"] = 12288
        else:
            settings["chunk_size"] = 8192   # Smaller chunks untuk stability
        
        # Adjust memory threshold based on project size
        if total_files > 50000:
            settings["memory_threshold"] = 70  # More conservative for xlarge projects
        elif total_files > 10000:
            settings["memory_threshold"] = 75
        
        # Adjust batch size
        if total_files > 20000:
            settings["batch_size"] = 25  # Smaller batches for memory efficiency
        elif total_files > 5000:
            settings["batch_size"] = 35
        else:
            settings["batch_size"] = 50
        
        # Always enable progress tracking untuk large projects
        if total_files > 1000:
            settings["enable_progress_tracking"] = True
        
        # Adjust max file size based on memory pressure
        memory_info = memory_monitor.get_memory_info()
        system_percent = memory_info.get("system_percent", 0)
        
        if system_percent > 80:
            settings["max_file_size_mb"] = 5  # Stricter limit saat memory tinggi
        
        return settings
    
    def prioritize_files(self, file_paths: List[str]) -> List[str]:
        """Prioritize files untuk optimal processing order"""
        try:
            # Score files based on priority and size
            file_scores = []
            
            for file_path in file_paths:
                score = self.get_file_score(file_path)
                file_scores.append((file_path, score))
            
            # Sort by score (descending) and return prioritized list
            file_scores.sort(key=lambda x: x[1], reverse=True)
            return [fp[0] for fp in file_scores]
            
        except Exception as e:
            print(f"Error prioritizing files: {e}")
            return file_paths
    
    def get_file_score(self, file_path: str) -> float:
        """Calculate file score based on priority and size"""
        try:
            # Get file extension priority
            ext = os.path.splitext(file_path)[1].lower()
            priority = self.file_priorities.get(ext, 3)  # Default priority 3
            
            # Get file size (smaller files get slight priority boost)
            try:
                file_size = os.path.getsize(file_path)
                size_mb = file_size / (1024 * 1024)
                
                # Size adjustment (smaller files get slight boost)
                if size_mb < 1:
                    size_bonus = 1.0
                elif size_mb < 5:
                    size_bonus = 0.5
                else:
                    size_bonus = 0
                    
            except OSError:
                size_bonus = 0
            
            # Calculate final score
            score = priority + size_bonus
            return score
            
        except Exception:
            return 1.0  # Default low score
    
    def should_skip_file(self, file_path: str, settings: Dict) -> Tuple[bool, str]:
        """Check if file should be skipped based on smart filtering"""
        try:
            # Check file size
            try:
                file_size = os.path.getsize(file_path)
                max_size_mb = settings.get("max_file_size_mb", 10)
                
                if file_size > max_size_mb * 1024 * 1024:
                    return True, f"File too large ({file_size // 1024 // 1024}MB > {max_size_mb}MB)"
                
            except OSError:
                return True, "Cannot access file"
            
            # Check if binary file (if enabled)
            if settings.get("skip_binary_files", True):
                if self.is_binary_file(file_path):
                    return True, "Binary file skipped"
            
            # Check file extension priority
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.file_priorities:
                return True, f"Unsupported file type: {ext}"
            
            return False, "OK"
            
        except Exception as e:
            return True, f"Error checking file: {e}"
    
    def is_binary_file(self, file_path: str) -> bool:
        """Quick binary file detection"""
        try:
            with open(file_path, 'rb') as f:
                # Read first 1024 bytes
                sample = f.read(1024)
                
                # Check for null bytes
                if b'\x00' in sample:
                    return True
                
                # Check for high percentage of non-printable characters
                non_text = sum(1 for byte in sample if byte < 9 or (13 < byte < 32) or byte > 126)
                return non_text > len(sample) * 0.30
                
        except Exception:
            return True  # Assume binary if we can't read it
    
    def get_processing_order(self, folder_path: str, settings: Dict) -> List[str]:
        """Get optimized processing order untuk files"""
        try:
            file_paths = []
            
            # Collect all files
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    # Check if should skip
                    should_skip, reason = self.should_skip_file(file_path, settings)
                    if not should_skip:
                        file_paths.append(file_path)
            
            # Prioritize files
            prioritized_files = self.prioritize_files(file_paths)
            
            return prioritized_files
            
        except Exception as e:
            print(f"Error getting processing order: {e}")
            return []
    
    def estimate_processing_time(self, project_stats: Dict, settings: Dict) -> Dict:
        """Estimate processing time based on project analysis"""
        total_files = project_stats.get("total_files", 0)
        total_size_mb = project_stats.get("total_size_mb", 0)
        
        # Base estimates (files per second)
        if total_files < 100:
            base_rate = 50  # Small projects: 50 files/sec
        elif total_files < 1000:
            base_rate = 30  # Medium projects: 30 files/sec
        elif total_files < 10000:
            base_rate = 20  # Large projects: 20 files/sec
        else:
            base_rate = 10  # Very large projects: 10 files/sec
        
        # Adjust for system resources
        memory_info = memory_monitor.get_memory_info()
        system_percent = memory_info.get("system_percent", 0)
        
        if system_percent > 80:
            base_rate *= 0.5  # Reduce rate if memory pressure high
        elif system_percent > 70:
            base_rate *= 0.7
        
        # Calculate estimates
        processing_time_seconds = total_files / base_rate if base_rate > 0 else 0
        processing_time_minutes = processing_time_seconds / 60
        
        return {
            "estimated_files_per_second": base_rate,
            "estimated_total_time_seconds": processing_time_seconds,
            "estimated_total_time_minutes": processing_time_minutes,
            "estimated_total_time_hours": processing_time_minutes / 60,
            "project_category": project_stats.get("project_size_category", "unknown"),
            "memory_pressure": memory_monitor.get_memory_pressure()
        }


# Global instance
smart_filter = SmartFileFilter()


def analyze_and_recommend(folder_path: str) -> Dict:
    """Main function untuk analyze project dan get recommendations"""
    try:
        # Analyze project
        project_stats = smart_filter.analyze_project_size(folder_path)
        
        # Get processing settings
        settings = smart_filter.get_recommended_settings(project_stats)
        
        # Estimate processing time
        time_estimate = smart_filter.estimate_processing_time(project_stats, settings)
        
        # Combine results
        result = {
            "project_analysis": project_stats,
            "recommended_settings": settings,
            "time_estimate": time_estimate,
            "ready_for_processing": True
        }
        
        # Add warnings if needed
        warnings = []
        
        if project_stats.get("total_files", 0) > 50000:
            warnings.append("Very large project detected. Consider using distributed processing.")
        
        if project_stats.get("large_files", 0) > 10:
            warnings.append("Many large files detected. Processing may take significant time.")
        
        if time_estimate.get("estimated_total_time_hours", 0) > 2:
            warnings.append("Processing estimated to take > 2 hours. Use async mode recommended.")
        
        if warnings:
            result["warnings"] = warnings
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "ready_for_processing": False
        }
