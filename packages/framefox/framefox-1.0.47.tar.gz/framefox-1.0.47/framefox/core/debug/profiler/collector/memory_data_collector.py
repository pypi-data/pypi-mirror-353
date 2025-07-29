import gc
import psutil
import sys
import tracemalloc
from typing import Dict, Any
from framefox.core.debug.profiler.collector.data_collector import DataCollector

class MemoryDataCollector(DataCollector):
    name = "memory"

    def __init__(self):
        super().__init__("memory", "fa-list")
        self.data = {}
        self.process = psutil.Process()
        # ✅ AJOUT : Démarrer tracemalloc pour tracer les allocations
        if not tracemalloc.is_tracing():
            tracemalloc.start(10)  # 10 frames de stack trace

    def collect(self, request, response):
        """Collecte des informations détaillées sur la mémoire."""
        try:
            # Mémoire du processus
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()

            # ✅ AJOUT : Statistiques Python détaillées
            current, peak = tracemalloc.get_traced_memory()
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            # ✅ AJOUT : Compter les objets Python
            object_counts = {}
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                object_counts[obj_type] = object_counts.get(obj_type, 0) + 1

            # ✅ AJOUT : Top 10 des plus gros consommateurs
            memory_hogs = []
            for stat in top_stats[:10]:
                memory_hogs.append({
                    'file': stat.traceback.format()[0] if stat.traceback else 'Unknown',
                    'size_mb': stat.size / 1024 / 1024,
                    'count': stat.count
                })

            # ✅ AJOUT : Taille des plus gros objets
            largest_objects = sorted([
                (type(obj).__name__, sys.getsizeof(obj) / 1024 / 1024)
                for obj in gc.get_objects()
                if sys.getsizeof(obj) > 1024 * 1024  # > 1MB
            ], key=lambda x: x[1], reverse=True)[:10]

            self.data = {
                # Métriques existantes
                "memory_usage": memory_info.rss / 1024 / 1024,  # MB
                "peak_memory": memory_info.vms / 1024 / 1024,   # MB
                "memory_percent": memory_percent,
                
                # ✅ NOUVELLES MÉTRIQUES
                "python_current_mb": current / 1024 / 1024,
                "python_peak_mb": peak / 1024 / 1024,
                "gc_objects_count": len(gc.get_objects()),
                "object_types_count": len(object_counts),
                "top_object_types": dict(sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:15]),
                "memory_hotspots": memory_hogs,
                "largest_objects": largest_objects,
                
                # ✅ COLLECTE DE DÉCHETS
                "gc_stats": {
                    "collections": gc.get_stats(),
                    "garbage_count": len(gc.garbage)
                }
            }

        except Exception as e:
            self.data = {
                "error": str(e),
                "memory_usage": 0,
                "peak_memory": 0
            }

    def reset(self):
        """Reset avec nettoyage de mémoire."""
        # ✅ AJOUT : Forcer le garbage collection
        collected = gc.collect()
        self.data = {}