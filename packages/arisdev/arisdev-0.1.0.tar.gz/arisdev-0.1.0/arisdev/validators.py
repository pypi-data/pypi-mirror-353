import re
from datetime import datetime

class Validator:
    def __init__(self, message=None):
        self.message = message

    def validate(self, value):
        raise NotImplementedError

class Required(Validator):
    def __init__(self, message="Field ini wajib diisi"):
        super().__init__(message)

    def validate(self, value):
        if value is None or value == "":
            raise ValueError(self.message)
        return value

class Email(Validator):
    def __init__(self, message="Format email tidak valid"):
        super().__init__(message)
        self.pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def validate(self, value):
        if value and not self.pattern.match(value):
            raise ValueError(self.message)
        return value

class MinLength(Validator):
    def __init__(self, min_length, message=None):
        super().__init__(message or f"Minimal {min_length} karakter")
        self.min_length = min_length

    def validate(self, value):
        if value and len(value) < self.min_length:
            raise ValueError(self.message)
        return value

class MaxLength(Validator):
    def __init__(self, max_length, message=None):
        super().__init__(message or f"Maksimal {max_length} karakter")
        self.max_length = max_length

    def validate(self, value):
        if value and len(value) > self.max_length:
            raise ValueError(self.message)
        return value

class Regex(Validator):
    def __init__(self, pattern, message="Format tidak valid"):
        super().__init__(message)
        self.pattern = re.compile(pattern)

    def validate(self, value):
        if value and not self.pattern.match(value):
            raise ValueError(self.message)
        return value

class Number(Validator):
    def __init__(self, min_value=None, max_value=None, message=None):
        super().__init__(message or "Harus berupa angka")
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value):
        try:
            num = float(value)
            if self.min_value is not None and num < self.min_value:
                raise ValueError(f"Minimal {self.min_value}")
            if self.max_value is not None and num > self.max_value:
                raise ValueError(f"Maksimal {self.max_value}")
            return num
        except (TypeError, ValueError):
            raise ValueError(self.message)

class Date(Validator):
    def __init__(self, format="%Y-%m-%d", message=None):
        super().__init__(message or f"Format tanggal harus {format}")
        self.format = format

    def validate(self, value):
        try:
            return datetime.strptime(value, self.format)
        except (TypeError, ValueError):
            raise ValueError(self.message)

class Choice(Validator):
    def __init__(self, choices, message=None):
        super().__init__(message or "Pilihan tidak valid")
        self.choices = choices

    def validate(self, value):
        if value not in self.choices:
            raise ValueError(self.message)
        return value 