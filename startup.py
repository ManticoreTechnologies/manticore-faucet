# Import utilities
from utils import create_logger, welcome_message, config

# Create a logger
logger = create_logger()

# Import Flask
from flask import Flask

# Create flask application
app = Flask("Manticore Crypto Faucet")

# Print the welcome message
print(welcome_message)

# Initialize Flask-Limiter, allow 1000 requests a day and 200 per hour
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import os

# Use environment variables to get Redis host and port
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

redis_connection = Redis(host=redis_host, port=redis_port, db=0)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=f"redis://{redis_host}:{redis_port}/0",  # Use the Redis container
)

# CORS policy for local development
from flask_cors import CORS
CORS(app)

# Content Security Policy
csp = {
    'default-src': ['\'self\'', 'https://cdn.jsdelivr.net'],
    'script-src': ['\'self\'', 'https://cdn.jsdelivr.net'],
}

# Initialize Flask-Talisman with CSP
from flask_talisman import Talisman
talisman = Talisman(
    app,
    content_security_policy=csp,
    force_https=False,
)

import routes  # Import routes
