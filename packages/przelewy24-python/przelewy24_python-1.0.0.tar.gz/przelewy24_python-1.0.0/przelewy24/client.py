"""
Przelewy24 API Client

Main client class for interacting with Przelewy24 payment gateway.
"""

import hashlib
import json
import requests
from typing import Optional, Dict, Any

from .models import TransactionRequest, TransactionResponse, TransactionVerification, TransactionStatus
from .exceptions import APIError, AuthenticationError


class Przelewy24Client:
    """
    Main client for Przelewy24 API operations
    
    This client handles transaction registration, verification, and other
    payment-related operations with the Przelewy24 payment gateway.
    """
    
    # API endpoints
    SANDBOX_URL = "https://sandbox.przelewy24.pl"
    PRODUCTION_URL = "https://secure.przelewy24.pl"
    
    def __init__(
        self,
        merchant_id: int,
        pos_id: int,
        crc_key: str,
        api_key: Optional[str] = None,
        sandbox: bool = True
    ):
        """
        Initialize Przelewy24 client
        
        Args:
            merchant_id: Your Przelewy24 merchant ID
            pos_id: Your Przelewy24 POS ID (usually same as merchant_id)
            crc_key: Your CRC key for generating signatures
            api_key: Your API key for REST API operations
            sandbox: Whether to use sandbox environment (default: True)
        """
        self.merchant_id = merchant_id
        self.pos_id = pos_id
        self.crc_key = crc_key
        self.api_key = api_key
        self.sandbox = sandbox
        
        # Set base URL based on environment
        self.base_url = self.SANDBOX_URL if sandbox else self.PRODUCTION_URL
        
        # Setup session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Przelewy24-Python-SDK/1.0.0',
            'Content-Type': 'application/json'
        })
    
    def register_transaction(self, transaction: TransactionRequest) -> TransactionResponse:
        """Register a new transaction with Przelewy24"""
        
        # Set merchant/pos IDs and prepare payload
        transaction.merchant_id = self.merchant_id
        transaction.pos_id = self.pos_id
        payload = transaction.to_json_dict()
        payload['sign'] = self._generate_signature(payload, "register")
        
        # Make API request
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/transaction/register",
                json=payload,
                auth=(str(self.pos_id), self.api_key)
            )
            response.raise_for_status()
            response_data = response.json()
            return TransactionResponse.from_dict(response_data, sandbox=self.sandbox)
            
        except requests.RequestException as e:
            raise APIError(f"Failed to register transaction: {str(e)}")
        except json.JSONDecodeError as e:
            raise APIError(f"Failed to parse response: {str(e)}")
    
    def verify_transaction(self, verification: TransactionVerification) -> TransactionStatus:
        """Verify a transaction after payment completion"""
        
        if not self.api_key:
            raise AuthenticationError("API key is required for transaction verification")
        
        # Set merchant/pos IDs and prepare payload
        verification.merchant_id = self.merchant_id
        verification.pos_id = self.pos_id
        payload = verification.to_json_dict()
        payload['sign'] = self._generate_signature(payload, "verify")
        
        # Make API request
        try:
            response = self.session.put(
                f"{self.base_url}/api/v1/transaction/verify",
                json=payload,
                auth=(str(self.pos_id), self.api_key)
            )
            response.raise_for_status()
            response_data = response.json()
            return TransactionStatus.from_dict(response_data)
            
        except requests.RequestException as e:
            raise APIError(f"Failed to verify transaction: {str(e)}")
        except json.JSONDecodeError as e:
            raise APIError(f"Failed to parse response: {str(e)}")

    

    
    def _generate_signature(self, payload: Dict[str, Any], signature_type: str = "register") -> str:
        """Generate SHA-384 signature for JSON API requests"""
        
        # Create signature payload with required fields based on type
        if signature_type == "register":
            signature_payload = {
                "sessionId": payload.get("sessionId"),
                "merchantId": payload.get("merchantId"),
                "amount": payload.get("amount"),
                "currency": payload.get("currency"),
                "crc": self.crc_key
            }
        elif signature_type == "verify":
            signature_payload = {
                "sessionId": payload.get("sessionId"),
                "orderId": payload.get("orderId"),
                "amount": payload.get("amount"),
                "currency": payload.get("currency"),
                "crc": self.crc_key
            }
        else:
            raise ValueError(f"Unknown signature type: {signature_type}")
        
        # Convert to JSON string (compact, no spaces)
        json_string = json.dumps(signature_payload, separators=(',', ':'), ensure_ascii=False)
        
        # Generate SHA-384 hash
        return hashlib.sha384(json_string.encode('utf-8')).hexdigest()
    

 