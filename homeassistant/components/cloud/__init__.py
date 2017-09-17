"""Component to integrate the Home Assistant cloud."""
import asyncio
import json
import logging
import os

import voluptuous as vol

from . import http_api, iot
from .const import CONFIG_DIR, DOMAIN, SERVERS


REQUIREMENTS = ['warrant==0.2.0', 'AWSIoTPythonSDK==1.2.0']
DEPENDENCIES = ['http']
CONF_MODE = 'mode'
MODE_DEV = 'development'
MODE_STAGING = 'staging'
MODE_PRODUCTION = 'development'
DEFAULT_MODE = MODE_DEV

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_MODE, default=DEFAULT_MODE): vol.In(SERVERS),
    }),
}, extra=vol.ALLOW_EXTRA)
_LOGGER = logging.getLogger(__name__)


@asyncio.coroutine
def async_setup(hass, config):
    """Initialize the Home Assistant cloud."""
    mode = DEFAULT_MODE

    if DOMAIN in config:
        mode = config[DOMAIN][CONF_MODE]

    cloud = Cloud(hass, mode)

    yield from hass.async_add_job(cloud.initialize)

    hass.data[DOMAIN] = cloud

    yield from hass.async_add_job(iot.setup, hass, cloud)
    yield from http_api.async_setup(hass)
    return True


class Cloud:
    """Hold the state of the cloud connection."""

    def __init__(self, hass, mode):
        """Create an instance of Cloud."""
        self.hass = hass
        self.mode = mode
        self.email = None
        self.thing_name = None

        info = SERVERS[mode]
        self.cognito_client_id = info['cognito_client_id']
        self.user_pool_id = info['user_pool_id']
        self.region = info['region']
        self.api_base = info['api_base']
        self.iot_endpoint = info['iot_endpoint']

    @property
    def certificate_pem_path(self):
        """Get path to certificate pem."""
        return self.path('{}_iot_certificate.pem'.format(self.mode))

    @property
    def secret_key_path(self):
        """Get path to public key."""
        return self.path('{}_iot_secret.key'.format(self.mode))

    @property
    def user_info_path(self):
        """Get path to the stored auth."""
        return self.path('{}_auth.json'.format(self.mode))

    @property
    def iot_topic(self):
        """Return IoT topic of this instance."""
        return "topic/{}/#".format(self.thing_name)

    def initialize(self):
        """Initialize and load cloud info."""
        # Ensure config dir exists
        path = self.hass.config.path(CONFIG_DIR)
        if not os.path.isdir(path):
            os.mkdir(path)

        user_info = self.user_info_path
        if os.path.isfile(user_info):
            with open(user_info, 'rt') as file:
                info = json.loads(file.read())
                self.email = info['email']
                self.thing_name = info['thing_name']

    def connect(self):
        """Connect to the IoT broker."""
        self.is_connected = iot.setup(self.hass, self)

    def path(self, *parts):
        """Get config path inside cloud dir."""
        return self.hass.config.path(CONFIG_DIR, *parts)

    def logout(self):
        """Close connection and remove all credentials."""
        self.email = None
        self.thing_name = None
        for file in (self.certificate_pem_path, self.secret_key_path,
                     self.user_info_path):
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
        # TODO close connection
