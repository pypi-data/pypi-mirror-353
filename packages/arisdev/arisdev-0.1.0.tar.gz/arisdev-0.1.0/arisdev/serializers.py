from datetime import datetime
from .database import Model

class Serializer:
    def __init__(self, model_class):
        self.model_class = model_class
        self.fields = {}
        self.read_only_fields = set()
        self.write_only_fields = set()

    def field(self, name, read_only=False, write_only=False):
        def decorator(func):
            self.fields[name] = func
            if read_only:
                self.read_only_fields.add(name)
            if write_only:
                self.write_only_fields.add(name)
            return func
        return decorator

    def to_dict(self, instance, include_read_only=True):
        result = {}
        for name, func in self.fields.items():
            if name in self.read_only_fields and not include_read_only:
                continue
            result[name] = func(instance)
        return result

    def to_instance(self, data):
        instance = self.model_class()
        for name, func in self.fields.items():
            if name in self.write_only_fields and name in data:
                setattr(instance, name, data[name])
        return instance

class DateTimeField:
    def __init__(self, format="%Y-%m-%d %H:%M:%S"):
        self.format = format

    def to_dict(self, value):
        if isinstance(value, datetime):
            return value.strftime(self.format)
        return value

    def to_instance(self, value):
        if isinstance(value, str):
            return datetime.strptime(value, self.format)
        return value

class RelatedField:
    def __init__(self, serializer):
        self.serializer = serializer

    def to_dict(self, value):
        if value is None:
            return None
        return self.serializer.to_dict(value)

    def to_instance(self, value):
        if value is None:
            return None
        return self.serializer.to_instance(value)

class ListField:
    def __init__(self, field):
        self.field = field

    def to_dict(self, value):
        if value is None:
            return []
        return [self.field.to_dict(item) for item in value]

    def to_instance(self, value):
        if value is None:
            return []
        return [self.field.to_instance(item) for item in value] 