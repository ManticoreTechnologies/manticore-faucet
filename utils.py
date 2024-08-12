# Manticore Technologies LLC
# (c) 2024 
# Manticore Crypto Faucet
#       utils.py 


# Logging #
import logging
import colorlog
import os


def create_logger():
    logger = logging.getLogger(os.path.basename(__file__))

    # Set the logging level from the argument
    logger.setLevel(config['General']['log_level'])

    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a stream handler with color formatting
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = colorlog.ColoredFormatter(
        fmt=(
            "%(log_color)s%(asctime)s - %(name)-15s - %(levelname)-8s - %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
    fh = logging.FileHandler(config['Logging']['log_file'])
    fh.setLevel(config['General']['log_level'])

    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger

# Arguments #
import argparse

def parse_args():
    # Get the logging level argument
    parser = argparse.ArgumentParser(
        prog='Manticore Crypto Faucet',
        description='This cryptocurrency faucet is designed for Evrmore and Evrmore assets.',
        epilog='Manticore Technologies LLC'
    )
    parser.add_argument('--log-level', 
                        choices=['DEBUG', 'WARNING', 'CRITICAL', 'INFO', 'ERROR'], 
                        default='CRITICAL', 
                        help='Set the logging level (default: INFO)')

    return parser.parse_args()

# Settings #
import configparser
config = configparser.ConfigParser()
config.read('settings.conf')

# Welcome #
welcome_message =(
        "\n"
        "========================================\n"
        "         MANTICORE CRYPTO FAUCET        \n"
        "========================================\n"
        "  (c) 2024 Manticore Technologies LLC   \n"
        "----------------------------------------\n"
        "Welcome to the Manticore Crypto Faucet! \n"
        "This faucet is designed for Evrmore and Evrmore assets.\n"
        "----------------------------------------\n"
)
