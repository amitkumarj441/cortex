from django.db.models.signals import post_save
from django.dispatch import receiver
from worldbrain.cortex.models import Article
from worldbrain.cortex.search.indexes import ArticleIndex
from django.forms import model_to_dict


@receiver(post_save, sender=Article)
def my_handler(**kwargs):
    search = ArticleIndex()
    article = model_to_dict(kwargs['instance'], exclude=['id'])
    search.index(article, kwargs['instance'].id)
