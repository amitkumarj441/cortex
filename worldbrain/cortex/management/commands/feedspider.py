import pika

from django.core.management.base import BaseCommand

from worldbrain.cortex.models import Source, SourceStates

# Set up RabbitMQ connection
SPIDER_QUEUE = 'worldbrain-spider'
credentials = pika.PlainCredentials('worldbrain', 'worldbrain')
parameters = pika.ConnectionParameters('polisky.me', 5672, '/worldbrain',
                                       credentials)

# TODO use another server for RabbitMQ

rabbitmq_connection = pika.adapters.blocking_connection.BlockingConnection(
    parameters)
channel = rabbitmq_connection.channel()
channel.queue_declare(queue=SPIDER_QUEUE)


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_sources = Source.objects.all().filter(
            ready_for_crawling=True).filter(processed_spider='')
        for source in all_sources:
            channel.basic_publish(exchange='', routing_key=SPIDER_QUEUE,
                                  body='{domain_name};{id}'
                                  .format(domain_name=source.domain_name,
                                          id=source.id))
        channel.close()
