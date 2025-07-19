"""
Performance monitoring and metrics for MSPKit
"""
import time
import threading
from typing import Dict, Any, List
from collections import defaultdict, deque
import json

class PerformanceMonitor:
    """Monitor MSP communication performance and statistics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, Dict[str, Any]] = defaultdict(self._create_metrics_dict)
        self._lock = threading.Lock()
    
    def _create_metrics_dict(self) -> Dict[str, Any]:
        """Create a new metrics dictionary"""
        return {
            'count': 0,
            'total_time': 0.0,
            'errors': 0,
            'recent_times': deque(maxlen=100)
        }
        self._lock = threading.Lock()
        
    def start_timing(self, operation: str) -> str:
        """Start timing an operation"""
        timing_id = f"{operation}_{time.time()}"
        setattr(self, f"_start_{timing_id}", time.time())
        return timing_id
        
    def end_timing(self, timing_id: str, success: bool = True):
        """End timing an operation"""
        end_time = time.time()
        start_attr = f"_start_{timing_id}"
        
        if hasattr(self, start_attr):
            start_time = getattr(self, start_attr)
            duration = end_time - start_time
            delattr(self, start_attr)
            
            operation = timing_id.split('_')[0]
            
            with self._lock:
                metrics = self.metrics[operation]
                metrics['count'] += 1
                metrics['total_time'] += duration
                metrics['recent_times'].append(duration)
                
                if not success:
                    metrics['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self._lock:
            stats = {}
            
            for operation, metrics in self.metrics.items():
                if metrics['count'] > 0:
                    recent_times = list(metrics['recent_times'])
                    stats[operation] = {
                        'total_calls': metrics['count'],
                        'total_errors': metrics['errors'],
                        'error_rate': metrics['errors'] / metrics['count'],
                        'avg_time_ms': (metrics['total_time'] / metrics['count']) * 1000,
                        'recent_avg_ms': (sum(recent_times) / len(recent_times)) * 1000 if recent_times else 0,
                        'success_rate': (metrics['count'] - metrics['errors']) / metrics['count']
                    }
            
            return stats
    
    def export_stats(self, filename: str):
        """Export statistics to file"""
        stats = self.get_stats()
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)

# Global performance monitor instance
perf_monitor = PerformanceMonitor()
