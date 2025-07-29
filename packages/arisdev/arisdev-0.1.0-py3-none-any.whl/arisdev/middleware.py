"""
Middleware handler untuk ArisDev Framework
"""

class Middleware:
    """Middleware handler untuk ArisDev Framework"""
    
    def __init__(self):
        """Inisialisasi middleware"""
        self.middlewares = []
    
    def add(self, middleware):
        """Add middleware
        
        Args:
            middleware (callable): Middleware function
        """
        self.middlewares.append(middleware)
        return middleware
    
    def remove(self, middleware):
        """Remove middleware
        
        Args:
            middleware (callable): Middleware function
        """
        if middleware in self.middlewares:
            self.middlewares.remove(middleware)
    
    def clear(self):
        """Clear semua middleware"""
        self.middlewares.clear()
    
    def __call__(self, request):
        """Process middleware
        
        Args:
            request: Request object
        """
        for middleware in self.middlewares:
            response = middleware(request)
            if response:
                return response
        return None 