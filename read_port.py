import configparser

def get_port(config_path='settings.conf'):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config.get('General', 'port', fallback='8000')  # Default to 8000 if not found

if __name__ == '__main__':
    print(get_port())
