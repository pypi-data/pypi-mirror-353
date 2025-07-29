"""
Template handler untuk ArisDev Framework
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

class Template:
    """Template handler untuk ArisDev Framework"""
    
    def __init__(self, template_folder="templates"):
        """Inisialisasi template
        
        Args:
            template_folder (str): Folder untuk template
        """
        self.template_folder = template_folder
        self.env = Environment(
            loader=FileSystemLoader(template_folder),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render(self, template_name, **context):
        """Render template
        
        Args:
            template_name (str): Nama template
            **context: Context data
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_string(self, template_string, **context):
        """Render template string
        
        Args:
            template_string (str): Template string
            **context: Context data
        """
        template = self.env.from_string(template_string)
        return template.render(**context)
    
    def get_template(self, template_name):
        """Get template
        
        Args:
            template_name (str): Nama template
        """
        return self.env.get_template(template_name)
    
    def list_templates(self):
        """List semua template"""
        return self.env.list_templates()
    
    def exists(self, template_name):
        """Check apakah template ada
        
        Args:
            template_name (str): Nama template
        """
        return self.env.get_template(template_name) is not None
    
    def add_template(self, template_name, template_string):
        """Add template
        
        Args:
            template_name (str): Nama template
            template_string (str): Template string
        """
        template = self.env.from_string(template_string)
        self.env.globals[template_name] = template
    
    def add_global(self, name, value):
        """Add global variable
        
        Args:
            name (str): Nama variable
            value: Nilai variable
        """
        self.env.globals[name] = value
    
    def add_filter(self, name, filter_func):
        """Add filter
        
        Args:
            name (str): Nama filter
            filter_func (callable): Filter function
        """
        self.env.filters[name] = filter_func
    
    def add_test(self, name, test_func):
        """Add test
        
        Args:
            name (str): Nama test
            test_func (callable): Test function
        """
        self.env.tests[name] = test_func
    
    def add_function(self, name, func):
        """Add function
        
        Args:
            name (str): Nama function
            func (callable): Function
        """
        self.env.globals[name] = func 