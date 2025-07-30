"""
Custom exceptions for Przelewy24 SDK
"""


class Przelewy24Error(Exception):
    """Base exception class for all Przelewy24 related errors"""
    pass


class ValidationError(Przelewy24Error):
    """Raised when request data validation fails"""
    pass


class APIError(Przelewy24Error):
    """Raised when API request fails"""
    
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(Przelewy24Error):
    """Raised when authentication fails"""
    pass


class TransactionError(Przelewy24Error):
    """Raised when transaction processing fails"""
    pass 