"""Token management for authentication."""
import base64
import json
import hashlib
import datetime
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from drf_authenticator.exceptions import (
    TokenError,
    TokenExpiredError,
    InvalidTokenError,
    TokenTypeError,
    TokenDecodeError,
    TokenEncodeError
)


class TokenBackend:
    """Backend class for custom token generation and validation.
    
    This class handles the low-level operations of token generation, encryption,
    decryption, and validation using Fernet symmetric encryption.
    
    Attributes:
        secret_key (str): The secret key used for token encryption
        access_token_lifetime (int): Lifetime of access tokens in seconds
        refresh_token_lifetime (int): Lifetime of refresh tokens in seconds
        fernet (Fernet): Fernet instance for encryption/decryption
    """
    
    def __init__(self) -> None:
        """Initialize the token backend with configuration from settings."""
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
        """Generate an encrypted token with given payload and lifetime.
        
        Args:
            payload (Dict[str, Any]): The data to be encoded in the token
            lifetime (int): Token lifetime in seconds
            
        Returns:
            str: The encrypted token string
            
        Raises:
            TokenEncodeError: If token generation fails
        """
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
    
    def encode_access_token(self, user: User) -> str:
        """Generate access token for the user.
        
        Args:
            user (User): The user to generate token for
            
        Returns:
            str: The generated access token
            
        Raises:
            TokenEncodeError: If token generation fails
        """
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
    
    def encode_refresh_token(self, user: User) -> str:
        """Generate refresh token for the user.
        
        Args:
            user (User): The user to generate token for
            
        Returns:
            str: The generated refresh token
            
        Raises:
            TokenEncodeError: If token generation fails
        """
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
    
    def decode_token(self, token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
        """Decode and validate any type of token.
        
        Args:
            token (str): The token to decode
            expected_type (Optional[str]): Expected token type ('access' or 'refresh')
            
        Returns:
            Dict[str, Any]: The decoded token payload
            
        Raises:
            InvalidTokenError: If token is malformed
            TokenExpiredError: If token has expired
            TokenTypeError: If token type doesn't match expected_type
            TokenDecodeError: If token decoding fails
        """
        try:
            # Decode base64 token
            try:
                encrypted_data = base64.urlsafe_b64decode(token.encode())
            except Exception:
                raise InvalidTokenError("Invalid token format")
            
            # Decrypt the token
            try:
                decrypted_data = self.fernet.decrypt(encrypted_data)
                token_data = json.loads(decrypted_data)
            except Exception:
                raise TokenDecodeError("Failed to decrypt token")
            
            # Check expiration
            if token_data['exp'] < timezone.now().timestamp():
                raise TokenExpiredError()
            
            # Validate token type if specified
            if expected_type and token_data['payload']['type'] != expected_type:
                raise TokenTypeError(f"Expected {expected_type} token but got {token_data['payload']['type']}")
                
            return token_data['payload']
            
        except TokenError:
            # Re-raise any of our custom exceptions
            raise
        except Exception as e:
            raise TokenDecodeError(f"Failed to decode token: {str(e)}")
    
    def decode_access_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate an access token.
        
        Args:
            token (str): The access token to decode
            
        Returns:
            Dict[str, Any]: The decoded token payload
            
        Raises:
            TokenError: If token validation fails
        """
        return self.decode_token(token, expected_type='access')
    
    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a refresh token.
        
        Args:
            token (str): The refresh token to decode
            
        Returns:
            Dict[str, Any]: The decoded token payload
            
        Raises:
            TokenError: If token validation fails
        """
        return self.decode_token(token, expected_type='refresh')


class AuthToken:
    """Main class for token management.
    
    This class provides a high-level interface for token operations including
    generation and validation of both access and refresh tokens.
    """
    
    def __init__(self) -> None:
        """Initialize the AuthToken with a TokenBackend instance."""
        self.backend = TokenBackend()
    
    @staticmethod
    def get_access_token(user: User) -> str:
        """Get access token for user.
        
        Args:
            user (User): The user to generate token for
            
        Returns:
            str: The generated access token
        """
        backend = TokenBackend()
        return backend.encode_access_token(user)
    
    @staticmethod
    def get_refresh_token(user: User) -> str:
        """Get refresh token for user.
        
        Args:
            user (User): The user to generate token for
            
        Returns:
            str: The generated refresh token
        """
        backend = TokenBackend()
        return backend.encode_refresh_token(user)
    
    @staticmethod
    def validate_refresh_token(refresh_token: str) -> Dict[str, Any]:
        """Validate a refresh token and return its payload.
        
        Args:
            refresh_token (str): The refresh token to validate
            
        Returns:
            Dict[str, Any]: The decoded token payload
            
        Raises:
            TokenError: If token validation fails
        """
        backend = TokenBackend()
        return backend.decode_refresh_token(refresh_token)
    
    @staticmethod
    def validate_token(token: str) -> Dict[str, Any]:
        """Validate any type of token and return its payload.
        
        Args:
            token (str): The token to validate
            
        Returns:
            Dict[str, Any]: The decoded token payload
            
        Raises:
            TokenError: If token validation fails
        """
        backend = TokenBackend()
        return backend.decode_token(token)
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """Generate a new access token using a refresh token.
        
        Args:
            refresh_token (str): The refresh token to use
            
        Returns:
            str: The new access token
            
        Raises:
            TokenError: If refresh token is invalid or user not found
        """
        backend = TokenBackend()
        payload = backend.decode_refresh_token(refresh_token)
        
        try:
            user = User.objects.get(id=payload['user_id'])
            return backend.encode_access_token(user)
        except User.DoesNotExist:
            raise TokenError("User not found")