# Manticore Technologies LLC
# (c) 2024 
# Manticore Crypto Faucet
#       startup.py 

# Import utilities
from utils import create_logger, welcome_message, config

# Create a logger
logger = create_logger()

# Import flask
from flask import Flask

# Create flask application
app = Flask("Manticore Crypto Faucet")

# Print the welcome message
print(welcome_message)

# Initialize Flask-Limiter, allow 1000 requests a day and 200 per hour
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
redis_connection = Redis(host='localhost', port=6379, db=0)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379/0",  # Pointing Flask-Limiter to Redis
)

import routes

