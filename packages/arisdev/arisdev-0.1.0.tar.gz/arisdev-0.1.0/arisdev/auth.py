"""
Authentication handler untuk ArisDev Framework
"""

import bcrypt
import hashlib
import os
from jose import jwt
from datetime import datetime, timedelta
from functools import wraps
from .database import Model, Field

class User(Model):
    id = Field.Integer(primary_key=True, autoincrement=True)
    username = Field.String(unique=True)
    email = Field.String(unique=True)
    password_hash = Field.String()
    is_active = Field.Boolean(default=True)
    is_admin = Field.Boolean(default=False)
    created_at = Field.DateTime(default=datetime.now)

class Auth:
    """Authentication handler untuk ArisDev Framework"""
    
    def __init__(self, app, secret_key=None, algorithm="HS256", token_expire_minutes=30):
        """Inisialisasi auth
        
        Args:
            app: Framework instance
            secret_key (str): Secret key untuk JWT
            algorithm (str): Algorithm untuk JWT
            token_expire_minutes (int): Token expire dalam menit
        """
        self.app = app
        self.secret_key = secret_key or app.secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
        self.current_user = None

    def hash_password(self, password):
        """Hash password
        
        Args:
            password (str): Password
        """
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def check_password(self, password, hashed):
        """Check password
        
        Args:
            password (str): Password
            hashed (str): Hashed password
        """
        return bcrypt.checkpw(password.encode(), hashed)

    def create_user(self, username, email, password, is_admin=False):
        session = User.get_session(self.app.engine)
        user = User(
            username=username,
            email=email,
            password_hash=self.hash_password(password),
            is_admin=is_admin
        )
        return user.save(session)

    def authenticate(self, username, password):
        session = User.get_session(self.app.engine)
        user = User.first(session, username=username)
        if user and self.check_password(password, user.password_hash):
            return user
        return None

    def create_token(self, data):
        """Create JWT token
        
        Args:
            data (dict): Token data
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token):
        """Decode JWT token
        
        Args:
            token (str): JWT token
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

    def login(self, user):
        """Login user
        
        Args:
            user: User object
        """
        token = self.create_token({"sub": user.id})
        self.current_user = user
        return {"access_token": token, "token_type": "bearer"}

    def logout(self):
        self.current_user = None

    def required(self, f):
        """Decorator untuk route yang membutuhkan autentikasi
        
        Args:
            f (callable): Route function
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            request = args[0]
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return self.app.response.unauthorized()
            
            try:
                token = auth_header.split(" ")[1]
                data = self.decode_token(token)
                user_id = data.get("sub")
                if not user_id:
                    return self.app.response.unauthorized()
            except:
                return self.app.response.unauthorized()
            
            return f(*args, **kwargs)
        return decorated

    def verify_token(self, token):
        try:
            payload = self.decode_token(token)
            session = User.get_session(self.app.engine)
            user = User.get_by_id(session, int(payload["sub"]))
            if user and user.is_active:
                return user
        except:
            pass
        return None

    def login_required(self, f):
        def decorated_function(*args, **kwargs):
            if not self.current_user:
                return self.app.redirect("/login")
            return f(*args, **kwargs)
        return decorated_function

    def admin_required(self, f):
        def decorated_function(*args, **kwargs):
            if not self.current_user or not self.current_user.is_admin:
                return self.app.redirect("/login")
            return f(*args, **kwargs)
        return decorated_function 