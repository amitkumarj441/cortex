from multiprocessing import Process
from urllib.parse import urljoin, urlsplit, urlparse

import logging
import pika

from django.db import IntegrityError

from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

# Set up RabbitMQ connection
SPIDER_QUEUE = 'worldbrain-spider'
CREDENTIALS = pika.PlainCredentials('worldbrain', 'worldbrain')
CONNECTION_PARAMETERS = pika.ConnectionParameters('polisky.me', 5672,
                                                  '/worldbrain', CREDENTIALS,
                                                  socket_timeout=30)


class SourceSpider(CrawlSpider):
    name = 'sourcespider'

    def parse_item(self, response):

        body = response.body.decode('utf8')
        selector = Selector(text=body)

        url_exists_in_db = False

        try:
            new_url = AllUrl(source=self.source, url=response.url, html=body,
                             is_article=False)
            new_url.save()

        except IntegrityError as e:  # url already in the database
            LOGGER.info(e)
            url_exists_in_db = True

        except Exception as e:
            LOGGER.error(e)

        finally:

            if not url_exists_in_db:

                urls = selector.css('a').xpath('@href').extract()

                for url in urls:

                    split = urlsplit(url)

                    base = ''

                    if not split.scheme:
                        base = 'http://'

                    if not split.netloc:
                        base += self.domain_name

                    url = urljoin(base, url)

                    yield Request(url=url)

    rules = (
        Rule(LxmlLinkExtractor(allow=(r'.{,200}', r'[^\?]*')),
             follow=True,
             callback='parse_item'),
    )

    def __init__(self, msg):
        """
        Create a spider for domain name contained in {msg}. The {id} in the
        message is used to retrieve the corresponding database object.
        :param msg: {bytes}, Format '{domain_name};{id}'
        """

        from ..models import Source  # for tests

        super(CrawlSpider, self).__init__(self)

        splitted = msg.split(b';')

        domain_name = str(splitted[0], 'utf8')

        self.domain_name = urlparse(domain_name).netloc
        self.id = int(splitted[1])
        self.start_urls = [domain_name]
        self.allowed_domains = [self.domain_name]
        self.source = None

        try:
            self.source = Source.objects.get(id=self.id)
        except Exception as e:
            LOGGER.error('Source for {domain_name} not found: {e}'.format(
                domain_name=self.domain_name, e=e))
            raise CloseSpider(e)

        self._compile_rules()


def run_spider(domain_name):
    crawler_process = CrawlerProcess()
    crawler_process.crawl(SourceSpider, domain_name)
    crawler_process.start()


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
        return pika.SelectConnection(CONNECTION_PARAMETERS,
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, connection):
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
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.queue_declare(self.on_queue_declareok, SPIDER_QUEUE)

    def on_channel_closed(self, channel, reply_code, reply_text):
        LOGGER.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def on_queue_declareok(self, method_frame):
        self.start_consuming()

    def start_consuming(self):
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         SPIDER_QUEUE,
                                                         no_ack=True)

    def on_consumer_cancelled(self, method_frame):
        if self._channel:
            self._channel.close()

    @staticmethod
    def on_message(channel, basic_deliver, properties, body):

        process = Process(target=run_spider, args=(body,))

        sourceid = int(body.split(b';')[1])

        try:
            source = Source.objects.get(id=sourceid)
        except Exception as e:
            LOGGER.error(e)
            return

        try:
            process.start()
        except Exception as e:
            LOGGER.error(e)
            source.fail(e)
        else:
            source.crawl()
        finally:
            source.save()

    def stop_consuming(self):
        if self._channel:
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, frame):
        self.close_channel()

    def close_channel(self):
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def test_run(self):
        self._connection = self.connect()
        self._connection.add_timeout(.1, self.test_stop)
        self._connection.ioloop.start()

    def test_stop(self):
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.stop()

    def stop(self):
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()

    def close_connection(self):
        self._connection.close()


def main():
    logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    domain_consumer = DomainConsumer()
    try:
        domain_consumer.run()
    except KeyboardInterrupt:
        domain_consumer.stop()


if __name__ == '__main__':
    import django

    django.setup()
    from ..models import AllUrl, Source

    main()
