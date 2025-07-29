# framefox/core/middleware/middlewares/memory_cleanup_middleware.py
import gc
import random
from starlette.middleware.base import BaseHTTPMiddleware
from framefox.core.di.service_container import ServiceContainer

class MemoryCleanupMiddleware(BaseHTTPMiddleware):
    """Middleware pour nettoyer la mémoire périodiquement."""
    
    def __init__(self, app, cleanup_interval: int = 20):
        super().__init__(app)
        self.request_count = 0
        self.cleanup_interval = cleanup_interval

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        self.request_count += 1
        
        # ✅ NETTOYAGE PÉRIODIQUE : Tous les X requêtes
        if self.request_count % self.cleanup_interval == 0:
            try:
                container = ServiceContainer()
                container.cleanup_memory()
                
                # Garbage collection système
                collected = gc.collect()
                
                # Log optionnel pour monitoring
                if collected > 0:
                    print(f"🧹 Memory cleanup: {collected} objects collected")
                    
            except Exception as e:
                # Ne pas interrompre la requête pour un nettoyage
                pass
        
        return response