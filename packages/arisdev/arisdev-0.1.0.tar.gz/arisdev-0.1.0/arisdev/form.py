"""
Form handler untuk ArisDev Framework
"""

class Field:
    """Field untuk form"""
    
    def __init__(self, required=False, default=None, validators=None):
        """Inisialisasi field
        
        Args:
            required (bool): Apakah field wajib diisi
            default: Nilai default
            validators (list): List validator
        """
        self.required = required
        self.default = default
        self.validators = validators or []
        self.value = None
        self.errors = []
    
    def validate(self, value):
        """Validate field value
        
        Args:
            value: Field value
        """
        self.value = value
        self.errors = []
        
        if self.required and not value:
            self.errors.append("Field ini wajib diisi")
            return False
        
        for validator in self.validators:
            if not validator(value):
                self.errors.append(validator.message)
                return False
        
        return True
    
    class String:
        """String field"""
        
        def __init__(self, required=False, default=None, min_length=None, max_length=None, pattern=None):
            """Inisialisasi string field
            
            Args:
                required (bool): Apakah field wajib diisi
                default (str): Nilai default
                min_length (int): Minimal panjang
                max_length (int): Maksimal panjang
                pattern (str): Regex pattern
            """
            self.required = required
            self.default = default
            self.min_length = min_length
            self.max_length = max_length
            self.pattern = pattern
    
    class Integer:
        """Integer field"""
        
        def __init__(self, required=False, default=None, min_value=None, max_value=None):
            """Inisialisasi integer field
            
            Args:
                required (bool): Apakah field wajib diisi
                default (int): Nilai default
                min_value (int): Minimal nilai
                max_value (int): Maksimal nilai
            """
            self.required = required
            self.default = default
            self.min_value = min_value
            self.max_value = max_value
    
    class Float:
        """Float field"""
        
        def __init__(self, required=False, default=None, min_value=None, max_value=None):
            """Inisialisasi float field
            
            Args:
                required (bool): Apakah field wajib diisi
                default (float): Nilai default
                min_value (float): Minimal nilai
                max_value (float): Maksimal nilai
            """
            self.required = required
            self.default = default
            self.min_value = min_value
            self.max_value = max_value
    
    class Boolean:
        """Boolean field"""
        
        def __init__(self, required=False, default=False):
            """Inisialisasi boolean field
            
            Args:
                required (bool): Apakah field wajib diisi
                default (bool): Nilai default
            """
            self.required = required
            self.default = default
    
    class Email:
        """Email field"""
        
        def __init__(self, required=False, default=None):
            """Inisialisasi email field
            
            Args:
                required (bool): Apakah field wajib diisi
                default (str): Nilai default
            """
            self.required = required
            self.default = default
    
    class URL:
        """URL field"""
        
        def __init__(self, required=False, default=None):
            """Inisialisasi URL field
            
            Args:
                required (bool): Apakah field wajib diisi
                default (str): Nilai default
            """
            self.required = required
            self.default = default
    
    class Date:
        """Date field"""
        
        def __init__(self, required=False, default=None, format="%Y-%m-%d"):
            """Inisialisasi date field
            
            Args:
                required (bool): Apakah field wajib diisi
                default (str): Nilai default
                format (str): Format tanggal
            """
            self.required = required
            self.default = default
            self.format = format
    
    class DateTime:
        """DateTime field"""
        
        def __init__(self, required=False, default=None, format="%Y-%m-%d %H:%M:%S"):
            """Inisialisasi datetime field
            
            Args:
                required (bool): Apakah field wajib diisi
                default (str): Nilai default
                format (str): Format datetime
            """
            self.required = required
            self.default = default
            self.format = format
    
    class File:
        """File field"""
        
        def __init__(self, required=False, allowed_extensions=None, max_size=None):
            """Inisialisasi file field
            
            Args:
                required (bool): Apakah field wajib diisi
                allowed_extensions (list): List ekstensi yang diizinkan
                max_size (int): Maksimal ukuran file (bytes)
            """
            self.required = required
            self.allowed_extensions = allowed_extensions
            self.max_size = max_size

class Form:
    """Form handler untuk ArisDev Framework"""
    
    def __init__(self, data=None):
        """Inisialisasi form
        
        Args:
            data (dict): Form data
        """
        self.data = data or {}
        self.errors = {}
        self.valid = False
    
    def validate(self):
        """Validate form"""
        self.errors = {}
        self.valid = True
        
        for name, field in self.__class__.__dict__.items():
            if isinstance(field, Field):
                value = self.data.get(name)
                if not field.validate(value):
                    self.errors[name] = field.errors
                    self.valid = False
        
        return self.valid
    
    def is_valid(self):
        """Check apakah form valid"""
        return self.valid
    
    def get_errors(self):
        """Get form errors"""
        return self.errors
    
    def get_value(self, name):
        """Get field value
        
        Args:
            name (str): Field name
        """
        field = getattr(self.__class__, name, None)
        if isinstance(field, Field):
            return field.value
        return None
    
    def get_data(self):
        """Get form data"""
        return {
            name: field.value
            for name, field in self.__class__.__dict__.items()
            if isinstance(field, Field)
        } 