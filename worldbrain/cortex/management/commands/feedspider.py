import pika

from django.core.management.base import BaseCommand

from worldbrain.cortex.models import Source, SourceStates


# TODO use another server for RabbitMQ


class Command(BaseCommand):
    credentials = pika.PlainCredentials('worldbrain', 'worldbrain')
    parameters = pika.ConnectionParameters('polisky.me', 5672, '/worldbrain',
                                           credentials, socket_timeout=30)

    def __init__(self, queue='worldbrain-spider'):
        self.SPIDER_QUEUE = queue
        self.rabbitmq_connection = \
            pika.adapters.blocking_connection.BlockingConnection(
                self.parameters)
        self.channel = self.rabbitmq_connection.channel()
        self.channel.queue_declare(queue=self.SPIDER_QUEUE)

    def handle(self, *args, **options):
        self.all_sources = Source.objects.all().filter(
            state=SourceStates.READY.value)
        for source in self.all_sources:
            self.channel.basic_publish(exchange='',
                                       routing_key=self.SPIDER_QUEUE,
                                       body='{domain_name};{id}'
                                       .format(domain_name=source.domain_name,
                                               id=source.id))
        self.channel.close()
