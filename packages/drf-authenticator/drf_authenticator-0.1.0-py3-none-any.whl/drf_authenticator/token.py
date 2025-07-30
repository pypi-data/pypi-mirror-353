"""Generate token for authentication"""
import base64
import json
import hashlib
import datetime
from typing import Dict, Any
from cryptography.fernet import Fernet
from django.conf import settings
from django.utils import timezone
from drf_authenticator.exceptions import (
    TokenError,
    TokenExpiredError,
    InvalidTokenError,
    TokenTypeError,
    TokenDecodeError,
    TokenEncodeError
)


class TokenBackend:
    """Backend class for custom token generation and validation"""
    
    def __init__(self):
        self.secret_key = getattr(settings, 'AUTH_SECRET_KEY', settings.SECRET_KEY)
        try:
            # Generate a Fernet key from the secret key
            key = hashlib.sha256(self.secret_key.encode()).digest()
            self.fernet = Fernet(base64.urlsafe_b64encode(key))
        except Exception as e:
            raise TokenError(f"Failed to initialize token backend: {str(e)}")
            
        self.access_token_lifetime = getattr(settings, 'ACCESS_TOKEN_LIFETIME', 300)  # 5 minutes
        self.refresh_token_lifetime = getattr(settings, 'REFRESH_TOKEN_LIFETIME', 86400)  # 24 hours
    
    def _generate_token(self, payload: Dict[str, Any], lifetime: int) -> str:
        """Generate an encrypted token with given payload and lifetime"""
        try:
            now = timezone.now()
            token_data = {
                'payload': payload,
                'exp': (now + datetime.timedelta(seconds=lifetime)).timestamp(),
                'iat': now.timestamp()
            }
            json_data = json.dumps(token_data)
            encrypted_token = self.fernet.encrypt(json_data.encode())
            return base64.urlsafe_b64encode(encrypted_token).decode()
        except Exception as e:
            raise TokenEncodeError(f"Failed to generate token: {str(e)}")
    
    def encode_access_token(self, user) -> str:
        """Generate access token for the user"""
        try:
            payload = {
                'user_id': str(user.id),
                'username': user.username,
                'email': user.email,
                'type': 'access'
            }
            return self._generate_token(payload, self.access_token_lifetime)
        except TokenError:
            raise
        except Exception as e:
            raise TokenEncodeError(f"Failed to encode access token: {str(e)}")
    
    def encode_refresh_token(self, user) -> str:
        """Generate refresh token for the user"""
        try:
            payload = {
                'user_id': str(user.id),
                'type': 'refresh'
            }
            return self._generate_token(payload, self.refresh_token_lifetime)
        except TokenError:
            raise
        except Exception as e:
            raise TokenEncodeError(f"Failed to encode refresh token: {str(e)}")
    
    def decode_access_token(self, access_token: str) -> Dict[str, Any]:
        """Decode and validate the access token"""
        try:
            # Decode base64 token
            try:
                encrypted_data = base64.urlsafe_b64decode(access_token.encode())
            except Exception as e:
                raise InvalidTokenError(f"Expired or invalid token")
            
            # Decrypt the token
            try:
                decrypted_data = self.fernet.decrypt(encrypted_data)
                token_data = json.loads(decrypted_data)
            except Exception as e:
                raise TokenDecodeError(f"Expired or invalid token")
            
            # Check expiration
            if token_data['exp'] < timezone.now().timestamp():
                raise TokenExpiredError()
            
            # Validate token type
            if token_data['payload']['type'] != 'access':
                raise TokenTypeError()
                
            return token_data['payload']
            
        except TokenError:
            # Re-raise any of our custom exceptions
            raise
        except Exception as e:
            raise TokenDecodeError(f"Expired or invalid token")


class AuthToken:
    """Main class for token management"""
    
    def __init__(self):
        self.backend = TokenBackend()
    
    @staticmethod
    def get_access_token(user):
        """Get access token for user"""
        backend = TokenBackend()
        return backend.encode_access_token(user)
    
    @staticmethod
    def get_refresh_token(user):
        """Get refresh token for user"""
        backend = TokenBackend()
        return backend.encode_refresh_token(user)