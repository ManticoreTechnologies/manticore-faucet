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

# CORS policy for local development
from flask_cors import CORS
CORS(app) # Set CORS policy
# Set the Content Security Policy
csp = {
    'default-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
    ],
    'script-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
    ]
}
# Initialize Flask-Talisman with the CSP and enforce HTTPS
from flask_talisman import Talisman
talisman = Talisman(
    app,
    content_security_policy=csp,
    force_https=False,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000,
    strict_transport_security_include_subdomains=True,
    strict_transport_security_preload=True
)



import routes

