import gc
from starlette.middleware.base import BaseHTTPMiddleware

class MemoryCleanupMiddleware(BaseHTTPMiddleware):
    """Middleware pour nettoyer la mémoire après chaque requête."""
    
    def __init__(self, app, cleanup_interval: int = 10):
        super().__init__(app)
        self.request_count = 0
        self.cleanup_interval = cleanup_interval

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        self.request_count += 1
        
        # Nettoyage périodique
        if self.request_count % self.cleanup_interval == 0:
            # Nettoyer le cache du container
            from framefox.application import Application
            container = Application().container
            if hasattr(container, 'clear_resolution_cache_periodically'):
                container.clear_resolution_cache_periodically()
            
            # Forcer garbage collection
            collected = gc.collect()
            if collected > 0:
                print(f"🧹 Memory cleanup: collected {collected} objects")
        
        return response