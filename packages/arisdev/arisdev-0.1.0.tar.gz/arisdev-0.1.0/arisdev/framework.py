"""
Framework handler untuk ArisDev Framework
"""

import os
from typing import Dict, List, Any, Optional, Callable
from werkzeug.wrappers import Request, Response as WerkzeugResponse
from werkzeug.serving import run_simple
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix

from .response import Response
from .database import Database
from .template import Template
from .middleware import Middleware
from .form import Form
from .auth import Auth
from .cache import Cache
from .logger import Logger
from .websocket import WebSocket
from .background import BackgroundTasks
from .upload import Upload
from .api import API

class Framework:
    """Framework handler untuk ArisDev Framework"""
    
    def __init__(self, 
                 name: str = None,
                 template_folder: str = "templates",
                 static_folder: str = "static",
                 upload_folder: str = "uploads",
                 debug: bool = False,
                 secret_key: str = None,
                 database_url: str = None,
                 redis_url: str = None):
        """Inisialisasi framework
        
        Args:
            name (str): Application name
            template_folder (str): Template folder path
            static_folder (str): Static folder path
            upload_folder (str): Upload folder path
            debug (bool): Debug mode
            secret_key (str): Secret key for session
            database_url (str): Database URL
            redis_url (str): Redis URL
        """
        self.name = name or __name__
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.upload_folder = upload_folder
        self.debug = debug
        self.secret_key = secret_key or os.urandom(24)
        self.database_url = database_url
        self.redis_url = redis_url
        
        # Initialize components
        self.url_map = Map()
        self.view_functions = {}
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.error_handlers = {}
        
        # Initialize handlers
        self.response = Response(self)
        self.database = Database(self)
        self.template = Template(self)
        self.middleware = Middleware(self)
        self.form = Form(self)
        self.auth = Auth(self)
        self.cache = Cache(self)
        self.logger = Logger(self)
        self.websocket = WebSocket(self)
        self.background = BackgroundTasks(self)
        self.upload = Upload(self)
        self.api = API(self)
        
        # Create folders if not exists
        for folder in [template_folder, static_folder, upload_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def route(self, rule: str, methods: List[str] = None):
        """Decorator untuk menambahkan route
        
        Args:
            rule (str): URL rule
            methods (List[str]): HTTP methods
        """
        def decorator(f: Callable):
            self.add_url_rule(rule, f.__name__, f, methods)
            return f
        return decorator
    
    def add_url_rule(self, rule: str, endpoint: str, view_func: Callable, methods: List[str] = None):
        """Add URL rule
        
        Args:
            rule (str): URL rule
            endpoint (str): Endpoint name
            view_func (callable): View function
            methods (List[str]): HTTP methods
        """
        methods = methods or ["GET"]
        self.url_map.add(Rule(rule, endpoint=endpoint, methods=methods))
        self.view_functions[endpoint] = view_func
    
    def before_request(self, f: Callable):
        """Decorator untuk menambahkan before request handler
        
        Args:
            f (callable): Before request handler
        """
        self.before_request_funcs.append(f)
        return f
    
    def after_request(self, f: Callable):
        """Decorator untuk menambahkan after request handler
        
        Args:
            f (callable): After request handler
        """
        self.after_request_funcs.append(f)
        return f
    
    def errorhandler(self, code: int):
        """Decorator untuk menambahkan error handler
        
        Args:
            code (int): HTTP status code
        """
        def decorator(f: Callable):
            self.error_handlers[code] = f
            return f
        return decorator
    
    def handle_request(self, request: Request) -> WerkzeugResponse:
        """Handle request
        
        Args:
            request (Request): Request object
        """
        # Run before request handlers
        for func in self.before_request_funcs:
            response = func(request)
            if response is not None:
                return response
        
        # Match URL
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            view_func = self.view_functions[endpoint]
            response = view_func(request, **values)
        except HTTPException as e:
            response = self.handle_error(e)
        except Exception as e:
            if self.debug:
                raise
            response = self.handle_error(e)
        
        # Run after request handlers
        for func in self.after_request_funcs:
            response = func(request, response)
        
        return response
    
    def handle_error(self, error: Exception) -> WerkzeugResponse:
        """Handle error
        
        Args:
            error (Exception): Error object
        """
        if isinstance(error, HTTPException):
            code = error.code
        else:
            code = 500
        
        handler = self.error_handlers.get(code)
        if handler:
            return handler(error)
        
        if isinstance(error, HTTPException):
            return self.response.error(error.description, code)
        
        return self.response.error(str(error), 500)
    
    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = None):
        """Run application
        
        Args:
            host (str): Host
            port (int): Port
            debug (bool): Debug mode
        """
        debug = debug if debug is not None else self.debug
        
        # Add static files middleware
        app = SharedDataMiddleware(self, {
            "/static": self.static_folder
        })
        
        # Add proxy fix middleware
        app = ProxyFix(app)
        
        # Start background tasks
        self.background.start()
        
        # Run application
        run_simple(host, port, app, use_debugger=debug, use_reloader=debug)
    
    def __call__(self, environ: Dict[str, Any], start_response: Callable) -> List[bytes]:
        """WSGI application
        
        Args:
            environ (Dict[str, Any]): WSGI environment
            start_response (callable): WSGI start_response
        """
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response) 