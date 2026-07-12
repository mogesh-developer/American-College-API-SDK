"""
Custom Exceptions
"""


class AMCException(Exception):
    """Base Exception"""
    pass


class LoginError(AMCException):
    """Login Failed"""
    pass


class APIError(AMCException):
    """API Request Failed"""
    pass


class AuthenticationError(AMCException):
    """Invalid API Token"""
    pass
