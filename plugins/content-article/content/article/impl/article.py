'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for article.
'''

from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from content.article.api.article import IArticleService, Article
from content.article.meta.article import ArticleMapped
from json.decoder import JSONDecoder
from ally.container.ioc import injected
from content.packager.api.item import IItemService, Item, IItemContentService, \
    ItemContent, CLASS_TEXT
from ally.container import wire
from content.packager.api.content import IContentService, Content
from sqlalchemy.sql.functions import current_timestamp
from content.publisher.api.publisher import IContentPublisherService

# --------------------------------------------------------------------

@injected
@setup(IArticleService, name='articleService')
class ArticleServiceAlchemy(EntityServiceAlchemy, IArticleService):
    '''
    Implementation for @see: IArticleService
    '''

    preview_url = 'http://localhost:8000/article/%(guid)s';  wire.config('preview_url', doc='''The article preview URL''')

    itemService = IItemService; wire.entity('itemService')
    # item service used to convert article content to NewsML structure
    itemContentService = IItemContentService; wire.entity('itemContentService')
    # item content service used to convert article content to NewsML structure
    contentService = IContentService; wire.entity('contentService')
    # content service used to convert article content to NewsML structure
    contentPublisherService = IContentPublisherService; wire.entity('contentPublisherService')
    # content service used to publish the article content to the web

    def __init__(self):
        '''
        Construct the article service.
        '''
        EntityServiceAlchemy.__init__(self, ArticleMapped)

    def publish(self, id):
        '''
        Implementation of @see: IArticleService.publish
        '''
        article = EntityServiceAlchemy.getById(self, id)
        if article.PublishedOn is None:
            assert isinstance(article, Article)
            article.PublishedOn = current_timestamp()
            EntityServiceAlchemy.update(self, article)
            self.contentPublisherService.publish(article.Item)

    def unpublish(self, id):
        '''
        Implementation of @see: IArticleService.unpublish
        '''
        article = EntityServiceAlchemy.getById(self, id)
        if article.PublishedOn is not None:
            assert isinstance(article, Article)
            article.PublishedOn = None
            EntityServiceAlchemy.update(self, article)
            self.contentPublisherService.unpublish(article.Item)

    def getById(self, id):
        '''
        Implementation of @see: IArticleService.getById
        '''
        article = EntityServiceAlchemy.getById(self, id)
        params = dict(guid=article.Item)
        article.Preview = self.preview_url % params
        return article

    def getAll(self, offset, limit, detailed, q):
        '''
        Implementation of @see: IArticleService.getAll
        '''
        articles = EntityServiceAlchemy.getAll(self, offset, limit, detailed, q)

        for article in articles:
            assert isinstance(article, Article)
            params = dict(guid=article.Item)
            article.Preview = self.preview_url % params

        return articles

    def insert(self, article):
        '''
        Implementation of @see: IArticleService.publish
        '''
        assert isinstance(article, Article)
        rawContent = JSONDecoder().decode(article.Content)
        item = Item()
        item.ItemClass = CLASS_TEXT
        item.HeadLine = rawContent['Title']
        item.SlugLine = '-'.join(item.HeadLine.split())
        item.Version = 1
        article.Item = self.itemService.insert(item)
        for tag in ('Lead', 'Body'):
            content = Content()
            content.ResidRef = tag
            content.Content = rawContent[tag]
            id = self.contentService.insert(content)
            itemContent = ItemContent()
            itemContent.Item = item.GUId
            itemContent.Content = content.Id
            self.itemContentService.insert(itemContent)
        return EntityServiceAlchemy.insert(self, article)

    def update(self, article):
        pass

    def delete(self, id):
        pass
