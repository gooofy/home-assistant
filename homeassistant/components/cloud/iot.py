import asyncio
import os

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


KEEP_ALIVE = 30


def client_factory(cloud):
    """Create IoT client."""
    root_ca = os.path.join(os.path.dirname(__file__), 'aws_iot_root_cert.pem')

    client = AWSIoTMQTTClient(cloud.thing_name)
    client.configureEndpoint(cloud.iot_endpoint, 8883)
    client.configureCredentials(root_ca, cloud.secret_key_path,
                                cloud.certificate_pem_path)

    # client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    # client.configureDrainingFrequency(2)  # Draining: 2 Hz
    # client.configureConnectDisconnectTimeout(10)  # 10 sec
    # client.configureMQTTOperationTimeout(5)  # 5 sec
    return client


def setup(hass, cloud):
    """Setup the IoT connection."""

    if not os.path.isfile(cloud.secret_key_path) or \
            not os.path.isfile(cloud.certificate_pem_path):
        return False

    client = client_factory(cloud)

    def message_callback(mqtt_client, userdata, msg):
        """Handle IoT message."""
        hass.add_job(handle_message, hass, client, msg.topic, msg.payload)

    if not client.connect(keepAliveIntervalSecond=KEEP_ALIVE):
        return False

    print("SUBSCRIBING", cloud.iot_topic)
    client.subscribe(cloud.iot_topic, 1, handle_message)
    print("SUBSCRIBED!")
    return True


@asyncio.coroutine
def handle_message(hass, client, topic, payload):
    """Handle an incoming IoT message."""
    print("topic", topic)
    print("payload", payload)
