"""
Data models for Przelewy24 transactions
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from decimal import Decimal
import re

from .exceptions import ValidationError


@dataclass
class TransactionRequest:
    """
    Model for transaction registration request to Przelewy24
    
    Based on the official Przelewy24 REST API documentation for transaction registration.
    """
    
    # Required fields
    session_id: str
    amount: int  # Amount in grosze (1 PLN = 100 grosze)
    currency: str = "PLN"
    description: str = ""
    email: str = ""
    
    # These will be set automatically by the client
    merchant_id: Optional[int] = None
    pos_id: Optional[int] = None
    
    # Optional fields
    client: Optional[str] = None
    address: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "PL"
    phone: Optional[str] = None
    language: Optional[str] = "pl"
    method: Optional[int] = None
    url_return: Optional[str] = None
    url_status: Optional[str] = None
    url_cancel: Optional[str] = None  # Cancel URL - required by some configurations
    time_limit: Optional[int] = None
    channel: Optional[int] = None
    wait_for_result: Optional[bool] = None
    regulation_accept: Optional[bool] = None
    shipping: Optional[int] = None
    transfer_label: Optional[str] = None
    
    # Additional fields for mobile integration
    mobile_lib: Optional[int] = None
    sdk_version: Optional[str] = None
    
    # Additional fields from the new API
    encoding: Optional[str] = None
    method_ref_id: Optional[str] = None
    cart: Optional[list] = None
    additional: Optional[dict] = None
    
    def __post_init__(self):
        """Validate the transaction request data"""
        self._validate()
    
    def _validate(self):
        """Validate required fields and formats"""
        
        # Validate session_id
        if not self.session_id or len(self.session_id) > 100:
            raise ValidationError("session_id is required and must be max 100 characters")
        
        # Validate amount
        if not isinstance(self.amount, int) or self.amount <= 0:
            raise ValidationError("amount must be a positive integer (in grosze)")
        
        # Validate currency
        if self.currency not in ["PLN", "EUR", "GBP", "CZK"]:
            raise ValidationError("currency must be one of: PLN, EUR, GBP, CZK")
        
        # Validate email format
        if self.email and not self._is_valid_email(self.email):
            raise ValidationError("Invalid email format")
        
        # Validate language
        if self.language and self.language not in ["pl", "en", "de", "es", "it"]:
            raise ValidationError("language must be one of: pl, en, de, es, it")
        
        # Validate URLs
        if self.url_return and not self._is_valid_url(self.url_return):
            raise ValidationError("Invalid url_return format")
        
        if self.url_status and not self._is_valid_url(self.url_status):
            raise ValidationError("Invalid url_status format")
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None
    

    
    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for new JSON API format"""
        data = {}
        
        # Add all non-None fields using camelCase naming
        for key, value in self.__dict__.items():
            if value is not None:
                # Convert field names to JSON API format
                json_key = self._to_json_key(key)
                data[json_key] = value
        
        return data
    

    
    def _to_json_key(self, field_name: str) -> str:
        """Convert Python field names to camelCase"""
        # Common field mappings
        mapping = {
            'merchant_id': 'merchantId', 'pos_id': 'posId', 'session_id': 'sessionId',
            'url_return': 'urlReturn', 'url_status': 'urlStatus', 'url_cancel': 'urlCancel',
            'time_limit': 'timeLimit', 'wait_for_result': 'waitForResult',
            'regulation_accept': 'regulationAccept', 'transfer_label': 'transferLabel',
            'mobile_lib': 'mobileLib', 'sdk_version': 'sdkVersion',
            'method_ref_id': 'methodRefId'
        }
        return mapping.get(field_name, field_name)


@dataclass
class TransactionResponse:
    """
    Model for transaction registration response from Przelewy24
    """
    
    data: Optional[Dict[str, Any]] = None
    sandbox: bool = True
    
    @property
    def is_success(self) -> bool:
        """Check if the transaction registration was successful"""
        return self.data is not None and 'token' in self.data
    
    @property
    def payment_url(self) -> Optional[str]:
        """Get the payment URL for redirecting the user"""
        if not self.is_success:
            return None
        
        base_url = "https://sandbox.przelewy24.pl" if self.sandbox else "https://secure.przelewy24.pl"
        token = self.data['token']
        return f"{base_url}/trnRequest/{token}"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], sandbox: bool = True) -> 'TransactionResponse':
        """Create TransactionResponse from API response data"""
        return cls(data=data.get('data'), sandbox=sandbox)


@dataclass
class TransactionVerification:
    """
    Model for transaction verification request
    """
    
    session_id: str
    amount: int
    currency: str = "PLN"
    order_id: Optional[int] = None
    
    # These will be set automatically by the client
    merchant_id: Optional[int] = None
    pos_id: Optional[int] = None
    

    
    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for new JSON API format"""
        data = {
            'merchantId': self.merchant_id,
            'posId': self.pos_id,
            'sessionId': self.session_id,
            'amount': self.amount,
            'currency': self.currency
        }
        
        if self.order_id:
            data['orderId'] = self.order_id
            
        return data


@dataclass
class TransactionStatus:
    """
    Model for transaction status response
    """
    
    data: Optional[Dict[str, Any]] = None
    response_code: Optional[int] = None
    
    @property
    def is_success(self) -> bool:
        """Check if the transaction verification was successful"""
        if self.response_code == 0:
            return True
        if self.data and self.data.get('status') == 'success':
            return True
        return False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionStatus':
        """Create TransactionStatus from API response data"""
        return cls(
            data=data.get('data'),
            response_code=data.get('responseCode')
        ) 