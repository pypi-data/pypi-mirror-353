from rest_framework.exceptions import AuthenticationFailed, NotAcceptable, NotAuthenticated


class TokenError(Exception):
    """Base exception for all token-related errors"""
    pass


class TokenExpiredError(TokenError):
    """Raised when the token has expired"""
    def __init__(self, message="Token has expired"):
        self.message = message
        super().__init__(self.message)


class InvalidTokenError(TokenError):
    """Raised when the token is invalid or malformed"""
    def __init__(self, message="Invalid token"):
        self.message = message
        super().__init__(self.message)


class TokenTypeError(TokenError):
    """Raised when the token type is incorrect"""
    def __init__(self, message="Invalid token type"):
        self.message = message
        super().__init__(self.message)


class TokenDecodeError(TokenError):
    """Raised when token decoding fails"""
    def __init__(self, message="Failed to decode token"):
        self.message = message
        super().__init__(self.message)


class TokenEncodeError(TokenError):
    """Raised when token encoding fails"""
    def __init__(self, message="Failed to encode token"):
        self.message = message
        super().__init__(self.message)