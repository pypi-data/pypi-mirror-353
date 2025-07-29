"""
Request handler untuk ArisDev Framework
"""

from werkzeug.wrappers import Request as WerkzeugRequest
from werkzeug.datastructures import MultiDict
import json

class Request(WerkzeugRequest):
    """Request handler untuk ArisDev Framework"""
    
    def __init__(self, environ):
        """Inisialisasi request
        
        Args:
            environ (dict): WSGI environment
        """
        super().__init__(environ)
        self.form = MultiDict(self.form)
        self.files = MultiDict(self.files)
        self.args = MultiDict(self.args)
        self.cookies = MultiDict(self.cookies)
        self.headers = MultiDict(self.headers)
        self._json = None

    @property
    def json(self):
        """Get JSON data dari request body"""
        if self._json is None and self.is_json:
            self._json = json.loads(self.get_data(as_text=True))
        return self._json

    @property
    def is_json(self):
        """Check apakah request adalah JSON"""
        return self.mimetype == 'application/json'

    @property
    def is_xhr(self):
        """Check apakah request adalah AJAX"""
        return self.headers.get('X-Requested-With') == 'XMLHttpRequest'

    @property
    def is_secure(self):
        """Check apakah request menggunakan HTTPS"""
        return self.environ.get('wsgi.url_scheme') == 'https'

    @property
    def remote_addr(self):
        """Get IP address client"""
        return self.environ.get('REMOTE_ADDR')

    @property
    def user_agent(self):
        """Get user agent client"""
        return self.environ.get('HTTP_USER_AGENT')

    @property
    def referrer(self):
        """Get referrer URL"""
        return self.environ.get('HTTP_REFERER')

    @property
    def host(self):
        """Get host header"""
        return self.environ.get('HTTP_HOST')

    @property
    def method(self):
        """Get HTTP method"""
        return self.environ.get('REQUEST_METHOD')

    @property
    def path(self):
        """Get request path"""
        return self.environ.get('PATH_INFO')

    @property
    def query_string(self):
        """Get query string"""
        return self.environ.get('QUERY_STRING')

    @property
    def content_type(self):
        """Get content type"""
        return self.environ.get('CONTENT_TYPE')

    @property
    def content_length(self):
        """Get content length"""
        return self.environ.get('CONTENT_LENGTH')

    @property
    def accept_languages(self):
        """Get accept languages"""
        return self.environ.get('HTTP_ACCEPT_LANGUAGE')

    @property
    def accept_encodings(self):
        """Get accept encodings"""
        return self.environ.get('HTTP_ACCEPT_ENCODING')

    @property
    def accept_charsets(self):
        """Get accept charsets"""
        return self.environ.get('HTTP_ACCEPT_CHARSET')

    @property
    def accept_mimetypes(self):
        """Get accept mimetypes"""
        return self.environ.get('HTTP_ACCEPT')

    def get_json(self, default=None):
        return self.json if self.is_json else default

    def get_form(self, key, default=None):
        return self.form.get(key, default)

    def get_query(self, key, default=None):
        return self.args.get(key, default)

    def get_cookie(self, key, default=None):
        return self.cookies.get(key, default) 