"""

A safe way to handle your secret keys/password is saving them in environment variables.
Create a folder ~/vault to store secret files with sensitive information such as api credentials.
The key/value pairs in the file will be read as environment variable when Python program runs.
File content looks as follows:
    API_KEY=abc
    API_SECRET=123

"""

import os
from dotenv import load_dotenv


# dotenv_path = os.path.expanduser('C:/vault/.testnet_API_secret')
dotenv_path = 'C:/vault/.testnet_API_secret'

load_dotenv(dotenv_path=dotenv_path)

API_KEY = os.getenv('KEY')
print(API_KEY)

# TODO get api secret string
API_SECRET = os.getenv('SECRET')
print(API_SECRET)
