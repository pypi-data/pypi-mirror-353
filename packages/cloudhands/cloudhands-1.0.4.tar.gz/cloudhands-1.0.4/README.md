# CloudHands SDK

CloudHands SDK is a Python library for interacting with the CloudHands API. It provides tools for authentication, charging events, and retrieving transaction details.

## Installation

```bash
pip install cloudhands
```

## Usage

```python
# initialize with your API key
ch = Cloudhands(api_key=YOUR_API_KEY)

# Can now make calls to the Cloudhands SDK to interact with and query the site
ch.get_posts(some_user_id) # Get posts for a user
ch.text_post(title=some_title, content=some_content)
```

## Publish on pypi
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload dist/*
