# Django SQL Query Logger

django installable package for logger middleware

## Features

- **QueryLoggerMiddleware**: Logs request/response query details

## Installation

```bash
pip install django-sql-query-logger
```

## Usage

Add the middleware to your Django settings:

```python
MIDDLEWARE = [
    # ... other middleware
    "sql_query_middlewares.middlewares.QueryLoggerMiddleware",
    # ... other middleware
]
```

## Configuration

No additional configuration required. The middleware will automatically:

- Log request information to the Django logger
- Add processing time headers to responses
- Number of sql queries has done in request response cycle

## Requirements

- Django >= 3.2
- Python >= 3.8

## License

MIT License