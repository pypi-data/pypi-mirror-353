# FastSMS

**Lightning-Fast Messaging API for Modern Businesses**

FastSMS is a high-performance SMS API built with ReadyAPI (FastAPI) that provides businesses with a reliable, scalable, and easy-to-use messaging solution.

## Features

- ⚡ **Lightning Fast**: Built on ReadyAPI for maximum performance
- 🚀 **Easy Integration**: Simple REST API endpoints
- 📱 **SMS Messaging**: Send SMS messages programmatically
- 🔒 **Secure**: Built with security best practices
- 📊 **Scalable**: Designed to handle high-volume messaging
- 🐍 **Python 3.9+**: Modern Python support

## Quick Start

### Installation

```bash
pip install fastsms
```

### Basic Usage

```python
from fastsms import FastSMS

# Initialize the FastSMS client
client = FastSMS()

# Send an SMS
response = client.send_sms(
    to="+1234567890",
    message="Hello from FastSMS!"
)

print(response)
```

### Running the API Server

```bash
# Start the FastSMS server
uvicorn fastsms.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## Requirements

- Python 3.9 or higher
- ReadyAPI (FastAPI) >= 0.112.0
- Uvicorn >= 0.34.3

## Development

### Setting up for Development

```bash
# Clone the repository
git clone <repository-url>
cd FastSMS

# Install dependencies
pip install -e .

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact: dev.suliman@icloud.com

## Author

**Md Sulaiman** - [dev.suliman@icloud.com](mailto:dev.suliman@icloud.com)

---

*FastSMS - Making business messaging simple and fast.*
