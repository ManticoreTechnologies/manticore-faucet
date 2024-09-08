import redis
import json
from startup import app, limiter
from rpc import send_command
from utils import create_logger, config
from flask import jsonify, request
import time
import os

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
# Initialize Redis connection
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)  # Adjust host/port/db if necessary

# Initialize the logger
logger = create_logger()


def save_asset_to_redis(asset_name, asset_data):
    """
    Save asset data to Redis as JSON, excluding the balance.
    """
    try:
        asset_data_str = json.dumps(asset_data)  # Convert asset data to JSON string
        redis_client.set(f"asset:{asset_name}", asset_data_str)  # Save to Redis
        logger.debug(f"Asset {asset_name} saved to Redis.")
    except Exception as e:
        logger.error(f"Failed to save asset {asset_name} to Redis: {str(e)}")


def get_asset_from_redis(asset_name):
    """
    Retrieve asset data from Redis. Returns None if not found.
    """
    try:
        asset_data_str = redis_client.get(f"asset:{asset_name}")
        if asset_data_str:
            return json.loads(asset_data_str)  # Convert back to Python dict
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve asset {asset_name} from Redis: {str(e)}")
        return None


@app.route("/balance", methods=['GET'])
def balance():
    try:
        # Get the balances for all assets
        balances = send_command('listassetbalancesbyaddress', [config['General']['address']])
        
        # Get the EVR balance and add it to the balances dictionary
        evr_balance = send_command('getbalance')
        balances.update({'EVR': evr_balance})
        
        asset_details = {}
        
        # Loop through each asset and fetch asset data from Redis or the node
        for asset_name, balance in balances.items():
            try:
                # Try to load the asset data from Redis first
                asset_data = get_asset_from_redis(asset_name)
                
                if asset_data is None and asset_name != 'EVR':  # If not found in Redis, fetch from node
                    asset_data = send_command('getassetdata', [asset_name])
                    save_asset_to_redis(asset_name, asset_data)  # Save the asset data to Redis
                
                # Handle EVR separately as it's the native token
                if asset_name == 'EVR':
                    asset_data = {
                        'asset_name': 'EVR',
                        'balance': evr_balance,
                        'ipfs_hash': None,  # EVR doesn't have an IPFS hash
                        'details': 'Native Evrmore asset'
                    }
                
                # Add the balance to the asset_data
                asset_data['balance'] = balance
                
                # Store the combined asset data in the result dictionary
                asset_details[asset_name] = asset_data
            
            except Exception as e:
                logger.error(f"Failed to retrieve asset data for {asset_name}: {str(e)}")
        
        logger.debug(f'Received {len(asset_details)} asset balances and details')
        return jsonify(asset_details)
    
    except Exception as e:
        logger.critical(f'Failed to load faucet balances. Is the node running on port {config["Node"]["port"]}? Error: {e}')
        return jsonify({"error": "Failed to load faucet balances. Please try again later."}), 500


@app.route("/request", methods=['POST'])
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
