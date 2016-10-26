from django.core.management.base import BaseCommand
from worldbrain.cortex.models import Article
from worldbrain.cortex.search.indexes import ArticleIndex
from worldbrain.settings.base import logger


class Command(BaseCommand):
    help = 'Indexes the database in Elastic Search'

    def handle(self, *args, **options):
        try:
            values = ['id',
                      'title',
                      'url',
                      'links',
                      'authors',
                      'keywords',
                      'summary',
                      'text',
                      'domain_name']
            all_entries = Article.objects.values(*values)
            search = ArticleIndex()

            for row in all_entries:
                id = row['id']
                del row['id']
                search.index(row, id)

            logger.info('Successfully indexed db')

        except Exception as e:
            print('Failed to index db: ' + str(e))
