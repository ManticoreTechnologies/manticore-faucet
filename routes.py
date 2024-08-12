# Manticore Technologies LLC
# (c) 2024 
# Manticore Crypto Faucet
#       routes.py 

from startup import app, limiter
from rpc import send_command
from utils import create_logger, config
from flask import jsonify, request
import time

# Initialize the logger
logger = create_logger()

@app.route("/", methods=['POST'])
@limiter.limit(f"{config['General']['rate_limit']} per day")
def faucet():
    """
    Handle requests to the faucet endpoint, process the request parameters, 
    and transfer the specified asset to the provided address.

    Returns:
        Response: JSON response indicating success or failure.
    """
    # Retrieve and validate parameters from the request
    params = get_parameters()

    logger.debug("Parameters supplied: ")
    logger.debug(params)

    if params is None:
        logger.critical("Request for address faucet did not provide an address...")
        return jsonify({"error": "No parameters supplied. Please supply `address` and `assetName` in the POST body. "
                                 "For example BODY={'address': 'EcKYVcxZRUEWByoAtdHYNzE6DM2nr6ZGug', 'assetName': 'CYBER'}"}), 400

    # Validate the provided Evrmore address
    try:
        address = str(params.get('address'))
        if len(address) != 34:
            return jsonify({"error": f"'{address}' is an invalid Evrmore address. Please provide a valid Evrmore address."}), 400
    except Exception as e:
        logger.critical("Address was not provided. Please provide a valid Evrmore address.")
        return jsonify({"error": "Address was not provided. Please provide a valid Evrmore address."}), 400    

    # Validate the provided asset name
    try:
        assetName = str(params.get('assetName'))
    except Exception as e:
        logger.critical("Asset name not provided. Please provide a valid asset name.")
        return jsonify({"error": "Asset name was not provided. Please provide a valid asset name."}), 400

    # Attempt to transfer the asset
    try:
        assets = send_command('listassetbalancesbyaddress', [config["General"]["address"]])
        
        if assetName in assets:
            logger.info(f"Found {assetName} in faucet, processing faucet request")
            try:
                response = send_command('transfer', [assetName, 
                                                     float(config["General"]["amount"]), 
                                                     address, 
                                                     "QmVo5Kk5kNQ7qrDHM6VaYxwnqeHn7udKpRAHTLfMCr8HnA", 
                                                     round(time.time()), 
                                                     config["General"]["address"], 
                                                     config["General"]["address"]])
                
            except Exception as e:
                logger.critical(f"Failed to transfer {assetName} to address: {address}")
                return jsonify({"error": f"Failed to transfer {assetName} to {address}"}), 500
            return jsonify({"message": "Thanks! Your assets will be sent out shortly"}), 200
        elif assetName == "EVR":
            balance = send_command('getbalance', [])
            logger.info("Found EVR in faucet, processing faucet request")
            try:
                response = send_command('sendtoaddress', [address, float(config["General"]["amount"])])
                
            except Exception as e:
                logger.critical(f"Failed to send EVR to address: {address}")
                return jsonify({"error": f"Failed to send EVR to {address}"}), 500
            return jsonify({"message": "Thanks! Your EVR will be sent out shortly"}), 200
        else:
            logger.error(f"`{assetName}` does not exist in the faucet.")
            return jsonify({"error": f'`{assetName}` does not exist in the faucet'}), 400
    except Exception as e:
        logger.critical("Failed to list assets. Possible invalid username or password.")
        return jsonify({"error": "Invalid username or password"}), 500

def get_parameters():
    """
    Retrieves parameters from the incoming JSON request body.

    Returns:
        dict: Parameters extracted from the request body or an empty dictionary if none are found.
    """
    try:
        return request.json if request.json is not None else {}
    except Exception as e:
        logger.error("Failed to parse JSON from request body.")
        return None
