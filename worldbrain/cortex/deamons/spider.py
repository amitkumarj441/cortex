from multiprocessing import Process

import django
import datetime
import logging
import pika

from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

django.setup()
from ..models import AllUrl, Source, SourceStates

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

# Set up RabbitMQ connection
SPIDER_QUEUE = 'worldbrain-spider'
CREDENTIALS = pika.PlainCredentials('worldbrain', 'worldbrain')
CONNECTION_PARAMETERS = pika.ConnectionParameters('polisky.me', 5672,
                                                  '/worldbrain', CREDENTIALS)


class SourceSpider(CrawlSpider):
    name = b'sourcespider'
    rules = [
        Rule(LxmlLinkExtractor(allow=[r'.{,200}', r'[^\?]*']))
    ]

    def __init__(self, msg):
        """
        msg: {bytes}, Format '{domain_name};{id}'
        :param msg:
        """
        super(CrawlSpider, self).__init__(self)
        splitted = msg.split(b';')
        self.domain_name = str(splitted[0], 'utf8')
        self.id = int(splitted[1])
        self.start_urls = [self.domain_name]
        self.allowed_domains = [self.domain_name]
        self.source = None
        try:
            self.source = Source.objects.get(id=self.id)
        except Exception as e:
            LOGGER.error('Source for {domain_name} not found: {e}'.format(
                domain_name=self.domain_name, e=e))

    def parse(self, response):

        if not self.source:
            LOGGER.error('Can not parse {domain_name} - missing source'.format(
                domain_name=self.domain_name))
            return

        try:
            body = response.body
            selector = Selector(text=body)
            for url in selector.css('a').xpath('@href').extract():
                if '?' not in url and len(url) <= 200:
                    new_url = AllUrl(source=self.source, url=url, html=body,
                                     is_article=False)
                    new_url.save()
        except Exception as e:
            LOGGER.error(e)
            self.source.processed_spider = 'Failed {now}: {e}'.format(
                now=datetime.datetime.now, e=e)
            self.source.state = SourceStates.FAILED
        else:
            self.source.processed_spider = str(datetime.datetime.now())
            self.source.state = SourceStates.READY
        finally:
            try:
                self.source.save()
            except Exception as e:
                LOGGER.error(e)


def run_spider(domain_name):
    crawler_process = CrawlerProcess()
    crawler_process.crawl(SourceSpider, domain_name)
    crawler_process.start()


# Asynchronous message consumer
class DomainConsumer:
    """
    Asynchronous domain consumer retrieving domain names from RabbitMQ
    and starting spiders to obtain URLs from them and saving them into the
    database
    """

    def __init__(self):
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None

    def connect(self):
        LOGGER.info('Connecting to RabbitMQ')
        return pika.SelectConnection(CONNECTION_PARAMETERS,
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, connection):
        LOGGER.info('Connection opened: {conn}'.format(conn=connection))
        self._connection.add_on_close_callback(self.on_connection_closed)
        self.open_channel()

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning(
                'Connection closed {conn}, reopening in 5 seconds: '
                '({reply_code}) {reply_text}.'
                .format(reply_code=reply_code,
                        reply_text=reply_text,
                        conn=connection))
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        """
        Reconnect connection if closed
        """
        self._connection.ioloop.stop()
        if not self._closing:
            self._connection = self.connect()
            self._connection.ioloop.start()

    def open_channel(self):
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOGGER.info('Channel opened')
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.queue_declare(self.on_queue_declareok, SPIDER_QUEUE)

    def on_channel_closed(self, channel, reply_code, reply_text):
        LOGGER.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def on_queue_declareok(self, method_frame):
        LOGGER.info('Queue declared: {mf}'.format(mf=method_frame))
        self.start_consuming()

    def start_consuming(self):
        LOGGER.info('Issuing consumer related RPC commands')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         SPIDER_QUEUE,
                                                         no_ack=True)

    def on_consumer_cancelled(self, method_frame):
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    @staticmethod
    def on_message(channel, basic_deliver, properties, body):
        LOGGER.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        LOGGER.info('Channel: {channel}'.format(channel=channel))
        process = Process(target=run_spider, args=(body,))
        process.start()

    def stop_consuming(self):
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, frame):
        LOGGER.info(
            'RabbitMQ acknowledged the cancellation of the consumer {frame}'.
            format(frame=frame))
        self.close_channel()

    def close_channel(self):
        LOGGER.info('Closing the channel')
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        LOGGER.info('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        LOGGER.info('Stopped')

    def close_connection(self):
        LOGGER.info('Closing connection')
        self._connection.close()


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    domain_consumer = DomainConsumer()
    try:
        domain_consumer.run()
    except KeyboardInterrupt:
        domain_consumer.stop()


if __name__ == '__main__':
    main()
