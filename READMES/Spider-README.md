Goal
-
Exctracting *URL*s and their *html* contents for domains in the *Source* 
table and saving them into the *AllUrl* table

Input
-
Domain names from the *Source* table which are not processed by spider yet and
are ready for crawling

Output
-
Saves extracted *URL*s into the *AllUrl* table with:

- `source = Initial source domain`
- `url = URL`
- `html = HTML content for the URL`
- `is_article = False`
- `state = AllUrlStates.PENDING`
 
Updates the correspondent Source fields:

- `state = SourceStates.READY` if succeeded
- `state = SourceStates.FAILED` if failed
- `last_time_crawled = timestamp of successfull crawling` if succeeded
- `last_error_message = error message` if failed

Technical implementation
-

- Django management command within the __cortex__ app (*/cortex/management/commands/feedspider.py*):

    Run command: `python manage.py feedspider` [should be started 
    periodically as a cronjob]
    
    The command looks for sources which are not processed by spider and ready for crawling 
    and pushes their domain names into the __RabbitMQ__ message queue.
    
- __RabbitMQ__ message queue (currently running on my private server on *polisky.me*):

    *__vhost__: /worldbrain,__user__: worldbrain, __password__: worldbrain, __queue__: worldbarin*
    
    Domain names are queued in the queue and delivered to consumer as soon as available.
    
- A consumer daemon waiting for domain names in the queue (*/cortex/daemons/spider.py*):

    Run command: `./start_spider.sh` from within the *worldbrain/* directory
    
    The daemon is waiting for domain names in the message queue and 
    asynchronously starting crawler processes for each incoming domain name. 
    After crawling, the database is updated.
    
Further suggestions:
-

- Run *RabbitMQ* server on a dedicated server
- Start *spider* via *uWSGI*
- Make spider feeder a daemon process and trigger its handler on *Source*'s 
ready state transition via *HTTP*
    