import newspaper
import time
import datetime
import nltk

from .models import AllUrl, AllUrlStates, Article, ArticleStates


class ContentExtractor:

    def __init__(self):
        nltk.download('punkt')

    def extract_content(self):
        urls = AllUrl.objects.filter(state=AllUrlStates.PENDING.value)
        for entry in urls:
            try:
                article = self.extract_content_wrapper(entry)
                article.save()
            except Exception as e:
                print('Error extracting content from {url}: {e}'.format(
                    url=entry, e=e))
            else:
                entry.processed()
                entry.save()

    def extract_content_wrapper(self, url):
        start = time.time()
        article = newspaper.Article(url='')
        article.download(html=url.html)
        article.parse()
        article.nlp()

        article2 = Article()
        try:
            article2.url = url
            article2.title = article.title
            article2.text = article.text
            article2.keywords = str(article.keywords)
            article2.authors = str(article.authors)
            article2.tags = list(article.tags)
            article2.summary = article.summary
            # article2.links
            end = time.time()
            article2.parse_time = end - start
            article2.state = ArticleStates.EXTRACTED.value
            # article2.html = article.html
            # ISO Format is the standard of maintaining datetime
            article2.publish_date = article.publish_date.isoformat()
        except Exception as e:
            now = datetime.datetime.now().isoformat()
            article2.publish_date = now[:now.index('T')]
            print('Some fields may be missing: {e}'.format(e=e))
        return article2
