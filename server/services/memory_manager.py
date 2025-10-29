"""
Memory Manager untuk Large Project Optimization
"""

from __future__ import annotations

import gc
import logging
import os
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available. Memory monitoring will be limited.")


class MemoryMonitor:
    """Monitor system and process memory usage"""
    
    def __init__(self, warning_threshold: int = 80, critical_threshold: int = 90):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        self.last_gc_time = time.time()
        self.gc_interval = 30  # Force GC every 30 seconds during monitoring
    
    def add_callback(self, callback):
        """Add callback function to be called when memory thresholds are exceeded"""
        self.callbacks.append(callback)
    
    def get_memory_info(self) -> Dict[str, float]:
        """Get current memory information"""
        if PSUTIL_AVAILABLE:
            try:
                # System memory
                system_memory = psutil.virtual_memory()
                process_memory = psutil.Process(os.getpid()).memory_info()
                
                return {
                    "system_total": system_memory.total,
                    "system_available": system_memory.available,
                    "system_used": system_memory.used,
                    "system_percent": system_memory.percent,
                    "process_rss": process_memory.rss,
                    "process_vms": process_memory.vms,
                    "process_percent": psutil.Process(os.getpid()).memory_percent()
                }
            except Exception as e:
                logging.error(f"Error getting memory info: {e}")
        
        # Fallback for systems without psutil
        return {
            "system_total": 0,
            "system_available": 0,
            "system_used": 0,
            "system_percent": 0,
            "process_rss": 0,
            "process_vms": 0,
            "process_percent": 0
        }
    
    def get_memory_pressure(self) -> str:
        """Get current memory pressure level"""
        memory_info = self.get_memory_info()
        system_percent = memory_info.get("system_percent", 0)
        process_percent = memory_info.get("process_percent", 0)
        
        # Use the higher of system or process memory usage
        max_percent = max(system_percent, process_percent)
        
        if max_percent >= self.critical_threshold:
            return "critical"
        elif max_percent >= self.warning_threshold:
            return "warning"
        else:
            return "normal"
    
    def should_trigger_gc(self) -> bool:
        """Check if garbage collection should be triggered"""
        current_time = time.time()
        return (current_time - self.last_gc_time) >= self.gc_interval
    
    def force_gc(self):
        """Force garbage collection"""
        collected = gc.collect()
        self.last_gc_time = time.time()
        logging.info(f"Garbage collection freed {collected} objects")
        return collected
    
    def start_monitoring(self, interval: float = 5.0):
        """Start background memory monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    memory_pressure = self.get_memory_pressure()
                    
                    # Check if we need to trigger GC
                    if memory_pressure in ["warning", "critical"] or self.should_trigger_gc():
                        self.force_gc()
                    
                    # Call callbacks if thresholds are exceeded
                    if memory_pressure in ["warning", "critical"]:
                        for callback in self.callbacks:
                            try:
                                callback(memory_pressure, self.get_memory_info())
                            except Exception as e:
                                logging.error(f"Error in memory callback: {e}")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logging.error(f"Error in memory monitor: {e}")
                    time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logging.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop background memory monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logging.info("Memory monitoring stopped")
    
    def get_optimization_suggestions(self) -> list[str]:
        """Get suggestions for memory optimization"""
        suggestions = []
        memory_info = self.get_memory_info()
        system_percent = memory_info.get("system_percent", 0)
        process_percent = memory_info.get("process_percent", 0)
        
        if system_percent > 85:
            suggestions.append("System memory usage is high. Consider closing other applications.")
        
        if process_percent > 50:
            suggestions.append("Process memory usage is high. Consider reducing batch sizes.")
        
        if not PSUTIL_AVAILABLE:
            suggestions.append("Install psutil for better memory monitoring: pip install psutil")
        
        return suggestions


class ChunkProcessor:
    """Process large files in chunks to manage memory usage"""
    
    def __init__(self, chunk_size: int = 8192, max_memory_mb: int = 100):
        self.chunk_size = chunk_size
        self.max_memory_mb = max_memory_mb
        self.memory_monitor = MemoryMonitor()
    
    def process_file_chunks(self, file_path: str, processor_func) -> Tuple[bool, Optional[Exception]]:
        """Process file in chunks with memory management"""
        try:
            with open(file_path, 'rb') as f:
                while True:
                    # Read chunk
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    # Check memory pressure
                    memory_pressure = self.memory_monitor.get_memory_pressure()
                    if memory_pressure == "critical":
                        self.memory_monitor.force_gc()
                        time.sleep(0.1)  # Brief pause to let system recover
                    
                    # Process chunk
                    try:
                        processor_func(chunk)
                    except Exception as e:
                        logging.error(f"Error processing chunk: {e}")
                        return False, e
            
            return True, None
            
        except Exception as e:
            return False, e
    
    def estimate_file_memory_usage(self, file_path: str) -> int:
        """Estimate memory usage for processing a file"""
        try:
            file_size = os.path.getsize(file_path)
            # Rough estimation: file size + processing overhead
            return int(file_size * 1.2)
        except Exception:
            return 0
    
    def can_process_file(self, file_path: str) -> Tuple[bool, str]:
        """Check if file can be processed without exceeding memory limits"""
        estimated_usage = self.estimate_file_memory_usage(file_path)
        available_mb = self.get_available_memory_mb()
        
        if estimated_usage > (available_mb * 1024 * 1024):
            return False, f"File too large. Estimated: {estimated_usage // 1024 // 1024}MB, Available: {available_mb}MB"
        
        return True, "OK"
    
    def get_available_memory_mb(self) -> int:
        """Get available memory in MB"""
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                # Use 70% of available memory as safe limit
                return int((memory.available * 0.7) // 1024 // 1024)
            except Exception:
                pass
        
        # Fallback: assume 1GB available
        return 1024


class LargeProjectOptimizer:
    """Optimize processing for large projects"""
    
    def __init__(self, max_concurrent_files: int = 10, chunk_size: int = 8192):
        self.max_concurrent_files = max_concurrent_files
        self.chunk_size = chunk_size
        self.memory_monitor = MemoryMonitor()
        self.chunk_processor = ChunkProcessor(chunk_size)
        
        # Statistics
        self.files_processed = 0
        self.total_files_size = 0
        self.processing_start_time = None
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def start_project(self, project_name: str = "unknown"):
        """Start project processing with optimizations"""
        self.processing_start_time = time.time()
        self.files_processed = 0
        self.total_files_size = 0
        self.memory_monitor.start_monitoring()
        logging.info(f"Starting project optimization for: {project_name}")
    
    def end_project(self):
        """End project processing and cleanup"""
        if self.processing_start_time:
            elapsed = time.time() - self.processing_start_time
            rate = self.files_processed / elapsed if elapsed > 0 else 0
            
            logging.info(f"Project completed: {self.files_processed} files, {rate:.1f} files/sec")
        
        self.memory_monitor.stop_monitoring()
    
    def get_processing_recommendations(self, total_files: int, total_size_mb: float) -> list[str]:
        """Get processing recommendations for large projects"""
        recommendations = []
        
        memory_info = self.memory_monitor.get_memory_info()
        system_percent = memory_info.get("system_percent", 0)
        
        if total_files > 10000:
            recommendations.append("Large project detected. Consider using async processing.")
        
        if total_size_mb > 1000:  # 1GB
            recommendations.append("Large total size detected. Enable streaming processing.")
        
        if system_percent > 70:
            recommendations.append("High system memory usage. Close unnecessary applications.")
        
        if total_files > self.max_concurrent_files * 10:
            recommendations.append(f"Consider reducing concurrent files from {self.max_concurrent_files}")
        
        return recommendations
    
    def optimize_for_large_files(self, files: list[str]) -> list[str]:
        """Optimize file processing order for large files"""
        # Sort files by size (largest first) to manage memory better
        try:
            file_sizes = [(f, os.path.getsize(f)) for f in files]
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            return [f[0] for f in file_sizes]
        except Exception:
            return files
    
    def should_cleanup_memory(self) -> bool:
        """Check if memory cleanup is needed"""
        return (time.time() - self.last_cleanup_time) >= self.cleanup_interval
    
    def cleanup_memory(self):
        """Perform memory cleanup"""
        self.memory_monitor.force_gc()
        self.last_cleanup_time = time.time()
    
    def get_project_stats(self) -> Dict:
        """Get current project processing statistics"""
        if not self.processing_start_time:
            return {}
        
        elapsed = time.time() - self.processing_start_time
        rate = self.files_processed / elapsed if elapsed > 0 else 0
        memory_info = self.memory_monitor.get_memory_info()
        
        return {
            "files_processed": self.files_processed,
            "total_size_mb": self.total_files_size / 1024 / 1024,
            "elapsed_time": elapsed,
            "processing_rate": rate,
            "memory_info": memory_info,
            "memory_pressure": self.memory_monitor.get_memory_pressure()
        }


# Global instances
memory_monitor = MemoryMonitor()
large_project_optimizer = LargeProjectOptimizer()


def initialize_memory_optimization():
    """Initialize memory optimization system"""
    global memory_monitor, large_project_optimizer
    
    # Add warning callbacks
    def memory_warning_callback(pressure_level: str, memory_info: Dict):
        if pressure_level == "critical":
            logging.warning("CRITICAL: Memory usage very high. Consider reducing processing load.")
        elif pressure_level == "warning":
            logging.info("Memory usage high. Garbage collection triggered.")
    
    memory_monitor.add_callback(memory_warning_callback)
    
    logging.info("Memory optimization system initialized")


def optimize_memory_for_large_project(project_info: Dict) -> Dict[str, any]:
    """Get memory optimization recommendations for a project"""
    recommendations = {
        "memory_settings": {},
        "processing_settings": {},
        "warnings": [],
        "suggestions": []
    }
    
    # Get project size estimation
    total_files = project_info.get("estimated_files", 0)
    total_size_mb = project_info.get("estimated_size_mb", 0)
    
    # Memory-based recommendations
    memory_info = memory_monitor.get_memory_info()
    system_percent = memory_info.get("system_percent", 0)
    
    if system_percent > 80:
        recommendations["warnings"].append("High system memory usage detected")
        recommendations["memory_settings"]["gc_frequency"] = "high"
        recommendations["memory_settings"]["chunk_size"] = "small"
    
    if total_files > 50000:
        recommendations["suggestions"].append("Very large project. Consider distributed processing.")
    
    if total_size_mb > 5000:  # 5GB
        recommendations["suggestions"].append("Large total size. Use streaming processing.")
    
    # Get processing recommendations
    processing_recs = large_project_optimizer.get_processing_recommendations(total_files, total_size_mb)
    recommendations["suggestions"].extend(processing_recs)
    
    return recommendations


# Initialize on module load
initialize_memory_optimization()
