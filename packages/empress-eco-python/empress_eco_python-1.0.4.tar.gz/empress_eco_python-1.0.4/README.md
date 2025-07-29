# empress-eco-python

Official Python SDK for the Empress Platform - Auto-generated from 3,452+ business functions.

## Installation

```bash
pip install empress-eco-python
```

## Usage

```python
import empress_sdk
from empress_sdk.api.default_api import DefaultApi
from empress_sdk.configuration import Configuration

config = Configuration(
    host='https://tkyoamipcnoimlxxtkuh.supabase.co/functions/v1',
    api_key={'X-API-Key': 'emp_your_key_here'}
)

api = DefaultApi(empress_sdk.ApiClient(config))

# Create a customer
response = api.business_logic_post({
    'doctype': 'Customer',
    'operation': 'create',
    'data': {
        'name': 'Acme Corporation',
        'email': 'contact@acme.com'
    }
})
```

## Features

- **3,452+ Business Functions** - Complete business automation
- **Auto-generated** - Always up-to-date with latest API
- **Type Hints** - Full type annotation support
- **Pay-per-use** - $0.02 per API call, no subscriptions

## Documentation

Full documentation: https://docs.empress-platform.com/sdk/python
