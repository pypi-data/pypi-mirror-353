"""
Response handler untuk ArisDev Framework
"""

from werkzeug.wrappers import Response as WerkzeugResponse
from werkzeug.datastructures import Headers
import json

class Response(WerkzeugResponse):
    """Response handler untuk ArisDev Framework"""
    
    def __init__(self, response=None, status=200, headers=None, mimetype=None,
                 content_type=None, direct_passthrough=False):
        """Inisialisasi response
        
        Args:
            response: Response data
            status (int): HTTP status code
            headers (dict): HTTP headers
            mimetype (str): MIME type
            content_type (str): Content type
            direct_passthrough (bool): Direct passthrough mode
        """
        if isinstance(response, (dict, list)):
            response = json.dumps(response)
            mimetype = mimetype or "application/json"
        super().__init__(response, status, headers, mimetype, content_type,
                        direct_passthrough)

    def set_cookie(self, key, value="", max_age=None, expires=None, path="/", domain=None, secure=False, httponly=False):
        self.headers.add("Set-Cookie", self._make_cookie(key, value, max_age, expires, path, domain, secure, httponly))

    def _make_cookie(self, key, value, max_age, expires, path, domain, secure, httponly):
        cookie = [f"{key}={value}"]
        if max_age is not None:
            cookie.append(f"Max-Age={max_age}")
        if expires is not None:
            cookie.append(f"Expires={expires}")
        if path is not None:
            cookie.append(f"Path={path}")
        if domain is not None:
            cookie.append(f"Domain={domain}")
        if secure:
            cookie.append("Secure")
        if httponly:
            cookie.append("HttpOnly")
        return "; ".join(cookie)

    @classmethod
    def json(cls, data, status=200, headers=None):
        """Create JSON response
        
        Args:
            data: JSON data
            status (int): HTTP status code
            headers (dict): HTTP headers
        """
        return cls(
            json.dumps(data),
            status=status,
            headers=headers,
            mimetype='application/json'
        )
    
    @classmethod
    def text(cls, text, status=200, headers=None):
        """Create text response
        
        Args:
            text (str): Text data
            status (int): HTTP status code
            headers (dict): HTTP headers
        """
        return cls(
            text,
            status=status,
            headers=headers,
            mimetype='text/plain'
        )
    
    @classmethod
    def html(cls, html, status=200, headers=None):
        """Create HTML response
        
        Args:
            html (str): HTML data
            status (int): HTTP status code
            headers (dict): HTTP headers
        """
        return cls(
            html,
            status=status,
            headers=headers,
            mimetype='text/html'
        )
    
    @classmethod
    def redirect(cls, location, status=302, headers=None):
        """Create redirect response
        
        Args:
            location (str): Redirect location
            status (int): HTTP status code
            headers (dict): HTTP headers
        """
        if headers is None:
            headers = {}
        headers['Location'] = location
        return cls('', status=status, headers=headers)
    
    @classmethod
    def error(cls, message, status=400, headers=None):
        """Create error response
        
        Args:
            message (str): Error message
            status (int): HTTP status code
            headers (dict): HTTP headers
        """
        return cls.json({
            'error': message
        }, status=status, headers=headers)
    
    @classmethod
    def not_found(cls, message="Not Found", headers=None):
        """Create 404 response
        
        Args:
            message (str): Error message
            headers (dict): HTTP headers
        """
        return cls.error(message, status=404, headers=headers)
    
    @classmethod
    def forbidden(cls, message="Forbidden", headers=None):
        """Create 403 response
        
        Args:
            message (str): Error message
            headers (dict): HTTP headers
        """
        return cls.error(message, status=403, headers=headers)
    
    @classmethod
    def unauthorized(cls, message="Unauthorized", headers=None):
        """Create 401 response
        
        Args:
            message (str): Error message
            headers (dict): HTTP headers
        """
        return cls.error(message, status=401, headers=headers)
    
    @classmethod
    def server_error(cls, message="Internal Server Error", headers=None):
        """Create 500 response
        
        Args:
            message (str): Error message
            headers (dict): HTTP headers
        """
        return cls.error(message, status=500, headers=headers) 