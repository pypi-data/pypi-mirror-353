# Clients Package

This package provides a collection of Python client classes for interacting with various services.

## Installation

```bash
pip install pypClients
```

## Modules

Below is a summary of the modules and their main classes/functions:

### `clients/api_client.py`

- **ApiClient**  
    Base class for making HTTP requests to APIs. Handles authentication, request building, and response parsing.

### `clients/database_client.py`

- **DatabaseClient**  
    Provides methods to connect to and interact with SQL/NoSQL databases.

### `clients/email_client.py`

- **EmailClient**  
    Utility class for sending emails via SMTP or third-party providers.

### `clients/file_client.py`

- **FileClient**  
    Handles file operations such as upload, download, and storage management.

### `clients/utils.py`

- Utility functions used across client classes (e.g., configuration loading, logging).

## Usage Example

```python
from clients.api_client import ApiClient

client = ApiClient(base_url="https://api.example.com", api_key="your_api_key")
response = client.get("/endpoint")
print(response.json())
```

## License

This project is licensed under the MIT License.

---

*For detailed documentation, refer to the docstrings in each module.*
