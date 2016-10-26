import pika

from worldbrain.cortex.daemons.spider import DomainConsumer

SPIDER_QUEUE = 'worldbrain-spider'
CREDENTIALS = pika.PlainCredentials('worldbrain', 'worldbrain')
CONNECTION_PARAMETERS = pika.ConnectionParameters('polisky.me', 5672,
                                                  '/worldbrain', CREDENTIALS)

domain_consumer = DomainConsumer()

connection = pika.SelectConnection(CONNECTION_PARAMETERS)
domain_consumer._connection = connection


def test_connect():
    domain_consumer.connect()


def test_on_connection_open():
    domain_consumer.on_connection_open(connection)


def test_on_connection_closed():
    domain_consumer._closing = False
    domain_consumer.on_connection_closed(connection, '', '')

    domain_consumer._closing = True
    domain_consumer.on_connection_closed(connection, '', '')


def test_reconnect():
    domain_consumer.reconnect()


def test_open_channel():
    domain_consumer.open_channel()


def test_stop_consuming():
    domain_consumer.stop_consuming()


def test_on_message():
    domain_consumer.on_message(None, None, None, b'http://test.com;1')
