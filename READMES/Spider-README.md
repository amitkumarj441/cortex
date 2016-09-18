The Spider module consists of:

- Django management command within the __cortex__ app (*/cortex/management/commands/feedspider.py*):

    Run command: `python manage.py feedspider`
    
    The command looks for sources which are not processed by spider and ready for crawling 
    and pushes their domain names into the __RabbitMQ__ message queue.
    
- __RabbitMQ__ message queue (currently running on my private server on *polisky.me*):

    *__vhost__: /worldbrain,__user__: worldbrain, __password__: worldbrain, __queue__: worldbarin*
    
    Domain names are queued in the queue and delivered to consumer as soon as available.
    
- A consumer deamon waiting for domain names in the queue (*/cortex/deamons/spider.py*):

    Run command: `./start_spider.sh` from within the *worldbrain/* directory
    
    The deamon is waiting for domain names in the message queue and asynchronously 
    starting a crawler process in a spawned separated process for each domain name. After crawling,
    the database is updated.
    