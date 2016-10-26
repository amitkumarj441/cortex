import pytest
import pika

from worldbrain.cortex.daemons.spider import DomainConsumer, \
    SourceSpider, run_spider

from worldbrain.cortex.models import Source

# Set up RabbitMQ connection
SPIDER_QUEUE = 'worldbrain-spider'
CREDENTIALS = pika.PlainCredentials('worldbrain', 'worldbrain')
CONNECTION_PARAMETERS = pika.ConnectionParameters('polisky.me', 5672,
                                                  '/worldbrain', CREDENTIALS)

TEST_DOMAIN_NAME = 'http://funnymals.org'


def create_source():
    source = Source(domain_name=TEST_DOMAIN_NAME)
    source.save()


def get_source():
    create_source()
    return Source.objects.get(domain_name=TEST_DOMAIN_NAME)


def test_domain_consumer():
    try:
        domain_consumer = DomainConsumer()
        domain_consumer.test_run()
    except:
        assert 0 == 1


@pytest.mark.django_db
def test_run_spider():

    domain_name = 'funnymals.org'

    try:
        run_spider(domain_name)
    except Exception as e:
        assert 0 == 1


@pytest.mark.django_db
def test_source_spider():

    class TestResponse:
        url = 'http://funnymals.org'
        body = b'<html><a href="http://test.com"></a></html>'

    response = TestResponse()

    source = get_source()

    try:
        spider = SourceSpider('{domain_name};{id}'.format(
            domain_name=source.domain_name, id=source.id).encode('utf8'))
        parsed = spider.parse_item(response)
    except Exception:
        assert 0 == 1

    request_url = next(parsed).url

    assert request_url == 'http://test.com'
