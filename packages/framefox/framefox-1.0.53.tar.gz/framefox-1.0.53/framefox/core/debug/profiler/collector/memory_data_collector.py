import gc
import psutil
import tracemalloc
import time
from typing import Dict, Any
from framefox.core.debug.profiler.collector.data_collector import DataCollector

class MemoryDataCollector(DataCollector):
    name = "memory"

    def __init__(self):
        super().__init__("memory", "fa-memory")
        self.process = psutil.Process()
        self.start_memory = 0
        self.template_render_start = 0
        
        # ✅ INITIALISATION PRÉCOCE : Initialiser data dès le début
        self._initialize_data()
        
        # Démarrer tracemalloc seulement pour la mesure basique
        if not tracemalloc.is_tracing():
            tracemalloc.start(1)

    def _initialize_data(self):
        """Initialise les données de base immédiatement."""
        self.data = {
            # Métriques principales (valeurs par défaut)
            "memory_usage_mb": 0.0,
            "memory_percent": 0.0,
            "python_current_mb": 0.0,
            "python_peak_mb": 0.0,
            "gc_objects_count": 0,
            
            # Template rendering (sera rempli par le middleware)
            "template_memory_mb": 0.0,
            "template_render_time_ms": 0.0,
            
            # État simple
            "status": "unknown",
            "collected_at": time.time(),
            
            # Garbage collection basique
            "gc_generation_0": 0,
            "gc_generation_1": 0, 
            "gc_generation_2": 0,
        }

    def start_template_measurement(self):
        """Démarrer la mesure de mémoire avant le rendu de template."""
        self.template_render_start = tracemalloc.get_traced_memory()[0]
        gc.collect()  # Nettoyer avant la mesure

    def end_template_measurement(self) -> float:
        """Terminer la mesure et retourner la consommation en MB."""
        if self.template_render_start > 0:
            current = tracemalloc.get_traced_memory()[0]
            template_memory = (current - self.template_render_start) / 1024 / 1024
            return max(0, template_memory)  # Éviter les valeurs négatives
        return 0

    def collect(self, request, response):
        """Version ultra-simple - métriques essentielles seulement."""
        try:
            # ✅ MÉTRIQUES SYSTÈME RAPIDES
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # ✅ PYTHON MEMORY TRACKING
            current, peak = tracemalloc.get_traced_memory()

            # ✅ CALCUL SIMPLE DE L'USAGE
            current_mb = memory_info.rss / 1024 / 1024
            python_current_mb = current / 1024 / 1024
            python_peak_mb = peak / 1024 / 1024

            # ✅ SIMPLE GC COUNT
            gc_objects = len(gc.get_objects())

            # ✅ MISE À JOUR des données existantes (ne pas recréer)
            self.data.update({
                # Métriques principales
                "memory_usage_mb": round(current_mb, 2),
                "memory_percent": round(memory_percent, 1),
                "python_current_mb": round(python_current_mb, 2),
                "python_peak_mb": round(python_peak_mb, 2),
                "gc_objects_count": gc_objects,
                
                # ✅ CONSERVER les métriques de template déjà définies
                # "template_memory_mb": self.data.get("template_memory_mb", 0),
                # "template_render_time_ms": self.data.get("template_render_time_ms", 0),
                
                # État simple
                "status": "normal" if current_mb < 500 else "high",
                "collected_at": time.time(),
                
                # Garbage collection basique
                "gc_generation_0": gc.get_count()[0],
                "gc_generation_1": gc.get_count()[1], 
                "gc_generation_2": gc.get_count()[2],
            })

        except Exception as e:
            # ✅ MÊME EN CAS D'ERREUR : Garder la structure de base
            self.data.update({
                "error": str(e),
                "memory_usage_mb": 0,
                "memory_percent": 0,
                "python_current_mb": 0,
                "python_peak_mb": 0,
                "gc_objects_count": 0,
                "status": "error"
            })

    def add_template_metrics(self, template_memory_mb: float, render_time_ms: float):
        """Ajouter les métriques de template après le rendu."""
        # ✅ PLUS DE VÉRIFICATION : self.data existe toujours maintenant
        self.data["template_memory_mb"] = round(template_memory_mb, 2)
        self.data["template_render_time_ms"] = round(render_time_ms, 2)
        
        # ✅ LOG DE DEBUG AMÉLIORÉ
        import logging
        logger = logging.getLogger("MEMORY_COLLECTOR")
        logger.debug(f"Template metrics added: {template_memory_mb:.2f}MB, {render_time_ms:.2f}ms")

    def reset(self):
        """Reset simple."""
        self._initialize_data()  # ✅ Réinitialiser avec la structure de base
        self.template_render_start = 0