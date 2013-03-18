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
    ItemContent, CLASS_TEXT, QItemContent
from ally.container import wire
from content.packager.api.content import IContentService, Content
from sqlalchemy.sql.functions import current_timestamp
from content.publisher.api.publisher import IContentPublisherService
from sqlalchemy.exc import SQLAlchemyError
import json
from ally.support.sqlalchemy.util_service import handle
from ally.exception import InputError
from ally.internationalization import _

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
        article = self.getById(id)
        if article.PublishedOn is None:
            assert isinstance(article, Article)
            article.PublishedOn = current_timestamp()
            try: self.session().flush(article)
            except SQLAlchemyError as e: handle(e, article)
            self.contentPublisherService.publish(article.Item)

    def unpublish(self, id):
        '''
        Implementation of @see: IArticleService.unpublish
        '''
        article = self.getById(id)
        if article.PublishedOn is not None:
            assert isinstance(article, Article)
            article.PublishedOn = None
            try: self.session().flush(article)
            except SQLAlchemyError as e: handle(e, article)
            self.contentPublisherService.unpublish(article.Item)

    def search(self, text):
        '''
        Implementation of @see: IArticleService.search
        '''
        return self.getAll()

    def getById(self, id):
        '''
        Implementation of @see: IArticleService.getById
        '''
        article = super().getById(id)
        params = dict(guid=article.Item)
        article.Preview = self.preview_url % params
        return article

    def getAll(self, offset=None, limit=None, detailed=False, q=None):
        '''
        Implementation of @see: IArticleService.getAll
        '''
        articles = super().getAll(offset, limit, detailed, q)

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
        rawContent = json.loads(article.Content)
        try:
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
        except KeyError as e:
            raise InputError(_('Invalid article content: missing field %s' % e))
        return super().insert(article)

    def update(self, article):
        '''
        Implementation of @see: IArticleService.update
        '''
        assert isinstance(article, Article)
        # update the article content
        super().update(article)

        # update the item content
        item = self.itemService.getById(article.Item)
        assert isinstance(item, Item)
        rawContent = JSONDecoder().decode(article.Content)
        item.HeadLine = rawContent['Title']
        item.SlugLine = '-'.join(item.HeadLine.split())
        item.Version += 1
        self.itemService.update(item)
        q = QItemContent()
        q.item = article.Item
        contents = self.itemContentService.getAll(q=q)
        for c in contents:
            assert isinstance(c, Content)
            if rawContent.get(c.ResidRef):
                c.Content = rawContent[c.ResidRef]
                self.contentService.update(c)

        # if article was published republish the changes
        if article.PublishedOn is not None:
            self.contentPublisherService.publish(article.Item)

    def delete(self, id):
        '''
        Implementation of @see: IArticleService.delete
        '''
        self.unpublish(id)
        article = super().getById(id)
        self.itemService.delete(article.Item)
        return super().delete(id)
