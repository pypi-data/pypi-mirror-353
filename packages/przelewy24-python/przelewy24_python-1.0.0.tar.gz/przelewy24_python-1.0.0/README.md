# Przelewy24 Python SDK

[![PyPI version](https://badge.fury.io/py/przelewy24-python.svg)](https://badge.fury.io/py/przelewy24-python)
[![Python versions](https://img.shields.io/pypi/pyversions/przelewy24-python.svg)](https://pypi.org/project/przelewy24-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python SDK for integrating with the Przelewy24 payment gateway. This library provides a clean, type-safe interface for transaction registration, verification, and notification handling.

## 🚀 Features

- **Transaction Management**: Complete transaction lifecycle support
- **Secure Authentication**: Built-in signature validation and API authentication
- **Environment Support**: Seamless switching between sandbox and production
- **Type Safety**: Full type hints and data validation
- **Error Handling**: Comprehensive exception handling with detailed error messages
- **Notification Processing**: Automated webhook validation and processing
- **Connection Testing**: Built-in connectivity verification
- **Official API Compliance**: Based on official Przelewy24 REST API documentation

## 📦 Installation

Install the package using pip:

```bash
pip install przelewy24-python
```

## 🔧 Quick Start

### 1. Initialize the Client

```python
from przelewy24 import Przelewy24Client

# Initialize client for sandbox environment
client = Przelewy24Client(
    merchant_id=12345,
    pos_id=12345,  # Usually same as merchant_id
    crc_key="your-crc-key",
    api_key="your-api-key",  # Required for transaction verification
    sandbox=True  # Set to False for production
)
```

### 2. Register a Transaction

```python
from przelewy24 import TransactionRequest
import uuid

# Create transaction request
transaction = TransactionRequest(
    session_id=str(uuid.uuid4()),
    amount=1000,  # Amount in grosze (10.00 PLN)
    currency="PLN",
    description="Premium subscription",
    email="customer@example.com",
    client="John Doe",
    url_return="https://yoursite.com/payment/success",
    url_status="https://yoursite.com/payment/notification"
)

# Register transaction
try:
    response = client.register_transaction(transaction)
    
    if response.is_success:
        print(f"✅ Transaction registered successfully!")
        print(f"Payment URL: {response.payment_url}")
        # Redirect user to response.payment_url
    else:
        print(f"❌ Registration failed: {response.error}")
        
except Exception as e:
    print(f"🚨 Error: {e}")
```

### 3. Handle Payment Notifications

**Note**: Transaction verification requires an API key to be set in the client.

```python
from przelewy24 import TransactionVerification

def handle_payment_notification(request):
    """Handle incoming payment notification from Przelewy24"""
    
    # Extract notification data
    notification_data = request.form.to_dict()
    
    # Validate notification signature
    if not client.validate_notification(notification_data):
        return "Invalid signature", 400
    
    # Create verification request
    verification = TransactionVerification(
        session_id=notification_data['p24_session_id'],
        amount=int(notification_data['p24_amount']),
        currency=notification_data['p24_currency'],
        order_id=int(notification_data['p24_order_id'])
    )
    
    # Verify transaction with Przelewy24
    try:
        status = client.verify_transaction(verification)
        
        if status.is_success:
            # Payment confirmed - process the order
            process_successful_payment(notification_data)
            return "OK", 200
        else:
            # Payment verification failed
            handle_payment_failure(notification_data, status.error)
            return "OK", 200  # Always return OK to P24
            
    except Exception as e:
        # Log error and return OK to prevent retries
        log_error(f"Verification error: {e}")
        return "OK", 200
```

## ⚙️ Configuration

### Environment Variables

Configure the client using environment variables:

```python
import os
from przelewy24 import Przelewy24Client

client = Przelewy24Client(
    merchant_id=int(os.getenv('P24_MERCHANT_ID')),
    pos_id=int(os.getenv('P24_POS_ID', os.getenv('P24_MERCHANT_ID'))),  # Defaults to merchant_id
    crc_key=os.getenv('P24_CRC_KEY'),
    api_key=os.getenv('P24_API_KEY'),
    sandbox=os.getenv('P24_SANDBOX', 'false').lower() == 'true'
)
```

### Production vs Sandbox

```python
# Production environment
production_client = Przelewy24Client(
    merchant_id=12345,
    pos_id=12345,
    crc_key="your-production-crc-key",
    api_key="your-production-api-key",
    sandbox=False
)

# Sandbox environment (for testing)
sandbox_client = Przelewy24Client(
    merchant_id=12345,
    pos_id=12345,
    crc_key="your-sandbox-crc-key",
    api_key="your-sandbox-api-key",
    sandbox=True
)
```

## 🔍 Advanced Usage

### Custom Transaction Parameters

```python
transaction = TransactionRequest(
    session_id="unique-session-id",
    amount=2500,  # 25.00 PLN
    currency="PLN",
    description="Premium subscription - Annual plan",
    email="customer@example.com",
    client="John Doe",
    address="123 Main Street",
    zip="00-001",
    city="Warsaw",
    country="PL",
    phone="+48123456789",
    language="en",
    method=25,  # Specific payment method
    url_return="https://yoursite.com/payment/success",
    url_status="https://yoursite.com/webhook/przelewy24",
    time_limit=15,  # Payment time limit in minutes
    channel=3,  # Payment channel flags
    regulation_accept=True,
    transfer_label="Order #ORD-2024-001"
)
```

### Comprehensive Error Handling

```python
from przelewy24 import ValidationError, APIError, AuthenticationError

try:
    response = client.register_transaction(transaction)
    
except ValidationError as e:
    # Handle validation errors (invalid data format)
    print(f"❌ Validation error: {e}")
    # Fix data and retry
    
except AuthenticationError as e:
    # Handle authentication issues
    print(f"🔐 Authentication error: {e}")
    # Check credentials and configuration
    
except APIError as e:
    # Handle API-specific errors
    print(f"🌐 API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response_data}")
    # Handle based on status code
    
except Exception as e:
    # Handle unexpected errors
    print(f"🚨 Unexpected error: {e}")
    # Log for debugging
```

### Connection Testing

```python
# Test API connectivity
if client.test_connection():
    print("✅ Connection to Przelewy24 successful")
else:
    print("❌ Connection failed - check your configuration")
```

## 📚 API Reference

### Przelewy24Client

Main client class for API operations.

#### Constructor Parameters

- `merchant_id` (int): Your Przelewy24 merchant ID
- `pos_id` (int): Your Przelewy24 POS ID (usually same as merchant_id)
- `crc_key` (str): Your CRC key for signature generation
- `api_key` (str, optional): Your API key for REST API operations (required for verification)
- `sandbox` (bool): Use sandbox environment (default: True)

#### Methods

- `register_transaction(transaction: TransactionRequest) -> TransactionResponse`
- `verify_transaction(verification: TransactionVerification) -> TransactionStatus`
- `test_connection() -> bool`
- `validate_notification(notification_data: Dict[str, Any]) -> bool`

### TransactionRequest

Data model for transaction registration.

#### Required Parameters

- `session_id` (str): Unique session identifier
- `amount` (int): Amount in grosze (1 PLN = 100 grosze)
- `currency` (str): Currency code (PLN, EUR, GBP, CZK)
- `description` (str): Payment description
- `email` (str): Customer email address

#### Optional Parameters

- `client` (str): Customer name
- `address` (str): Customer address
- `zip` (str): ZIP/postal code
- `city` (str): City name
- `country` (str): Country code (default: "PL")
- `phone` (str): Phone number
- `language` (str): Interface language (pl, en, de, es, it)
- `method` (int): Specific payment method ID
- `url_return` (str): Return URL after payment
- `url_status` (str): Notification webhook URL
- `time_limit` (int): Payment time limit in minutes
- `channel` (int): Payment channel flags
- `regulation_accept` (bool): Regulation acceptance flag
- `transfer_label` (str): Transfer description

### TransactionResponse

Response object from transaction registration.

#### Properties

- `is_success` (bool): Indicates if registration was successful
- `token` (str): Transaction token (if successful)
- `payment_url` (str): URL for customer redirection
- `error` (str): Error message (if failed)
- `error_code` (int): Error code (if failed)

### TransactionVerification

Data model for transaction verification.

#### Required Parameters

- `session_id` (str): Session ID from notification
- `amount` (int): Amount from notification
- `currency` (str): Currency from notification
- `order_id` (int): Order ID from notification

### TransactionStatus

Response object from transaction verification.

#### Properties

- `is_success` (bool): Indicates if verification was successful
- `data` (dict): Verification response data
- `error` (str): Error message (if failed)
- `response_code` (int): HTTP response code

## 🛡️ Security Considerations

1. **Never expose credentials**: Keep your CRC key and merchant ID secure
2. **Use HTTPS**: Always use HTTPS for notification URLs
3. **Validate signatures**: Always validate notification signatures
4. **Environment separation**: Use different credentials for sandbox and production
5. **Error handling**: Don't expose sensitive information in error messages

## 🧪 Testing

This package is currently in active development. Comprehensive test coverage is planned for future releases. For now, you can test the functionality using the sandbox environment provided by Przelewy24.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Przelewy24 Official Documentation](https://developers.przelewy24.pl/)
- [Przelewy24 Support](https://www.przelewy24.pl/kontakt)
- [PyPI Package](https://pypi.org/project/przelewy24-python/)
- [GitHub Repository](https://github.com/ItsRaelx/PythonPrzelewy24)

## 📋 Changelog

### v1.0.0 (2024-12-XX)

- 🎉 Initial release
- ✅ Transaction registration and verification
- ✅ Notification handling and validation
- ✅ Sandbox and production environment support
- ✅ Comprehensive error handling
- ✅ Type hints and data validation
- ✅ Connection testing utilities

---

**Made with ❤️ for the Python community** 