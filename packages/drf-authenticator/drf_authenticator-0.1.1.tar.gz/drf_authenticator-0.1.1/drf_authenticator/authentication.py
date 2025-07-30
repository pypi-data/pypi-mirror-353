"""Handle authentication for users"""
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

from drf_authenticator.token import TokenBackend
from drf_authenticator.exceptions import (
    TokenError,
    TokenExpiredError,
    InvalidTokenError,
    TokenTypeError,
    TokenDecodeError
)


class RestAuthentication(authentication.BaseAuthentication):
    """Authentication class that validates Bearer tokens and authenticates users"""

    def authenticate(self, request):
        """Authenticate the user based on the Bearer token"""
        access_token = request.headers.get("Authorization")
        if not access_token:
            return None  # authentication did not succeed
        
        # Remove 'Bearer ' if present
        if not access_token.startswith('Bearer '):
            raise exceptions.AuthenticationFailed()

        access_token = access_token[7:]

        token = TokenBackend()
        try:
            decode_value = token.decode_access_token(access_token)
            
            if decode_value.get("email"):
                try:
                    user = User.objects.get(email=decode_value.get("email"))
                except User.DoesNotExist:
                    raise exceptions.AuthenticationFailed('No such user')
            
            elif decode_value.get("username"):
                try:
                    user = User.objects.get(username=decode_value.get("username"))
                except User.DoesNotExist:
                    raise exceptions.AuthenticationFailed('No such user')
            else:
                raise exceptions.AuthenticationFailed('Invalid token payload')
            
            return (user, None)  # authentication successful
            
        except TokenExpiredError as e:
            raise exceptions.AuthenticationFailed(str(e))
        except TokenTypeError as e:
            raise exceptions.AuthenticationFailed(str(e))
        except (InvalidTokenError, TokenDecodeError) as e:
            raise exceptions.AuthenticationFailed(str(e))
        except TokenError as e:
            raise exceptions.AuthenticationFailed(f"Authentication failed: {str(e)}")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Unexpected authentication error: {str(e)}")
