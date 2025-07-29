"""
Cache handler untuk ArisDev Framework
"""

import redis
import json
from datetime import datetime, timedelta

class Cache:
    """Cache handler untuk ArisDev Framework"""
    
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        """Inisialisasi cache
        
        Args:
            host (str): Redis host
            port (int): Redis port
            db (int): Redis database
            password (str): Redis password
        """
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
    
    def get(self, key):
        """Get value from cache
        
        Args:
            key (str): Cache key
        """
        value = self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    
    def set(self, key, value, expire=None):
        """Set value to cache
        
        Args:
            key (str): Cache key
            value: Cache value
            expire (int): Expire time in seconds
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.redis.set(key, value, ex=expire)
    
    def delete(self, key):
        """Delete value from cache
        
        Args:
            key (str): Cache key
        """
        self.redis.delete(key)
    
    def exists(self, key):
        """Check if key exists
        
        Args:
            key (str): Cache key
        """
        return self.redis.exists(key)
    
    def expire(self, key, seconds):
        """Set expire time for key
        
        Args:
            key (str): Cache key
            seconds (int): Expire time in seconds
        """
        self.redis.expire(key, seconds)
    
    def ttl(self, key):
        """Get time to live for key
        
        Args:
            key (str): Cache key
        """
        return self.redis.ttl(key)
    
    def clear(self):
        """Clear all cache"""
        self.redis.flushdb()
    
    def get_or_set(self, key, default, expire=None):
        """Get value from cache or set default
        
        Args:
            key (str): Cache key
            default: Default value
            expire (int): Expire time in seconds
        """
        value = self.get(key)
        if value is None:
            if callable(default):
                value = default()
            else:
                value = default
            self.set(key, value, expire)
        return value
    
    def increment(self, key, amount=1):
        """Increment value
        
        Args:
            key (str): Cache key
            amount (int): Increment amount
        """
        return self.redis.incr(key, amount)
    
    def decrement(self, key, amount=1):
        """Decrement value
        
        Args:
            key (str): Cache key
            amount (int): Decrement amount
        """
        return self.redis.decr(key, amount)
    
    def get_many(self, keys):
        """Get many values
        
        Args:
            keys (list): List of keys
        """
        values = self.redis.mget(keys)
        return {
            key: json.loads(value) if value else None
            for key, value in zip(keys, values)
        }
    
    def set_many(self, mapping, expire=None):
        """Set many values
        
        Args:
            mapping (dict): Key-value mapping
            expire (int): Expire time in seconds
        """
        pipe = self.redis.pipeline()
        for key, value in mapping.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            pipe.set(key, value, ex=expire)
        pipe.execute()
    
    def delete_many(self, keys):
        """Delete many values
        
        Args:
            keys (list): List of keys
        """
        self.redis.delete(*keys)
    
    def keys(self, pattern="*"):
        """Get keys matching pattern
        
        Args:
            pattern (str): Key pattern
        """
        return self.redis.keys(pattern)
    
    def close(self):
        """Close Redis connection"""
        self.redis.close() 