
class DatabaseCredentials:

    def __init__(self, config_file=None, config_dict=None):
        # check if config file is type configParser
        # must be config.ini for now - more compatability to come

        if not config_file and not config_dict:
            raise ValueError('config file is None')

        if config_file:
            db_creds = config_file.database_credentials
        elif config_dict:
            db_creds = config_dict

        self.type = db_creds.get('type')
        self.name = db_creds.get('name')
        self.user = db_creds.get('user')
        self.password = db_creds.get('password')
        self.connection = db_creds.get('connection')
    
    @staticmethod
    def uri_from_config(config_file=None, config_dict=None):
        if not config_file and not config_dict:
            return None

        db_creds = DatabaseCredentials(config_file=config_file, config_dict=config_dict)

        return f"{db_creds.type}://{db_creds.user}:{db_creds.password}@localhost:3306/{db_creds.name}"