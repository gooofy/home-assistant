"""Constants for the cloud component."""
DOMAIN = 'cloud'
CONFIG_DIR = '.cloud'
REQUEST_TIMEOUT = 10

SERVERS = {
    'development': {
        'cognito_client_id': '5ue1uhqbrbah5v1istsrt5tfci',
        'user_pool_id': 'us-east-1_6JB0r7TpZ',
        'region': 'us-east-1',
        'api_base': 'https://etjcgc8aq0.execute-api.us-east-1.amazonaws.com/dev/',
        'iot_endpoint': 'a2xa1v8c9macdh.iot.us-east-1.amazonaws.com'
    }
}
