'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for article.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import handle, buildLimits
from content.article.api.article import IArticleService, Article, QArticle, IArticleTargetTypeService
from content.article.api.search_provider import IArticleSearchProvider
from content.article.meta.article import ArticleMapped, ArticleTargetTypeMapped
from content.article.meta.target_type import TargetTypeMapped
from content.packager.api.item import IItemService, Item, CLASS_PACKAGE
from content.packager.api.item_content import IItemContentService, ItemContent, \
    QItemContent
from content.publisher.api.publisher import IContentPublisherService
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import current_timestamp
import json
from ally.api.extension import IterPart
from superdesk.user.api.user import IUserService
from urllib.parse import quote

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
    contentPublisherService = IContentPublisherService; wire.entity('contentPublisherService')
    # content service used to publish the article content to the web
    articleSearchProvider = IArticleSearchProvider; wire.entity('articleSearchProvider')
    # the search provider used to search the article list
    userService = IUserService; wire.entity('userService')
    # the user service used to set the creator
    authorService = IUserService; wire.entity('authorService')
    # the author service used to set the author
    
    def __init__(self):
        '''
        Construct the article service.
        '''
        super().__init__(ArticleMapped, QArticle)

    def publish(self, id):
        '''
        Implementation of @see: IArticleService.publish
        '''
        article = self.getById(id)
        assert isinstance(article, Article)
        # set article publish timestamp
        article.PublishedOn = current_timestamp()
        try: self.session().flush((article,))
        except SQLAlchemyError as e: handle(e, article)
        # publish the article content through the content publisher service
        self.contentPublisherService.publish(article.Item)

    def unpublish(self, id):
        '''
        Implementation of @see: IArticleService.unpublish
        '''
        article = self.getById(id)
        assert isinstance(article, Article)
        # unset article publish timestamp
        article.PublishedOn = None
        try: self.session().flush((article,))
        except SQLAlchemyError as e: handle(e, article)
        # publish the article content through the content publisher service
        self.contentPublisherService.unpublish(article.Item)

    def getById(self, id):
        '''
        Implementation of @see: IArticleService.getById
        '''
        article = super().getById(id)
        params = dict(guid=quote(article.Item, safe=''))
        article.Preview = self.preview_url % params
        return article

    def getAll(self, offset=None, limit=None, detailed=False, q=None):
        '''
        Implementation of @see: IArticleService.getAll
        '''
        sql, count = self.articleSearchProvider.buildQuery(self.session(), offset, limit, q)
        articles = sql.all()
        
        for article in articles:
            assert isinstance(article, Article)
            params = dict(guid=quote(article.Item, safe=''))
            article.Preview = self.preview_url % params

        return IterPart(articles, count, offset, limit) 
    
    def insert(self, article):
        '''
        Implementation of @see: IArticleService.publish
        '''
        assert isinstance(article, Article)

        # decode the JSON content
        rawContent = json.loads(article.Content)
        try:
            # create the corresponding item (@see IItemService)
            item = Item()
            item.ItemClass = CLASS_PACKAGE
            item.HeadLine = rawContent['Title']
            item.SlugLine = '-'.join(item.HeadLine.split())
            item.Version = 1
            item.Byline = self.authorService.getById(article.Author).FullName
            item.CreditLine = self.userService.getById(article.Creator).FullName
            article.Item = self.itemService.insert(item)

            # create the item content (@see IContentService, @see IItemContentService)
            for tag in ('Lead', 'Body'):
                content = ItemContent()
                content.Item = item.GUId
                content.ContentType = 'text/html'
                content.ResidRef = tag
                content.Content = rawContent[tag]
                id = self.itemContentService.insert(content)
        except KeyError as e:
            raise InputError(_('Invalid article content: missing field %s' % e))

        # insert the article content
        article = super().insert(article)
        
        self.articleSearchProvider.update(article)
        
        return article

    def update(self, article):
        '''
        Implementation of @see: IArticleService.update
        '''
        assert isinstance(article, Article)
        origArt = super().getById(article.Id)
        assert isinstance(origArt, Article)
        article.Item = origArt.Item
        article.PublishedOn = origArt.PublishedOn

        # update the article content
        super().update(article)

        # update the item content
        item = self.itemService.getById(article.Item)
        assert isinstance(item, Item)
        rawContent = json.loads(article.Content)
        item.HeadLine = rawContent['Title']
        item.SlugLine = '-'.join(item.HeadLine.split())
        item.Version += 1
        self.itemService.update(item)
        q = QItemContent()
        q.item = article.Item
        contents = self.itemContentService.getAll(q=q)
        for c in contents:
            assert isinstance(c, ItemContent)
            if rawContent.get(c.ResidRef):
                c.Content = rawContent[c.ResidRef]
                self.itemContentService.update(c)

        # if article was published republish the changes
        if article.PublishedOn is not None:
            self.contentPublisherService.publish(article.Item)
        
        self.articleSearchProvider.update(article)
            

    def delete(self, id):
        '''
        Implementation of @see: IArticleService.delete
        '''
        # unpublish the article from all outputs (e.g. web)
        self.unpublish(id)
        self.articleSearchProvider.delete(id)

        article = super().getById(id)
        # delete the article
        if super().delete(id):
            # delete the corresponding item
            self.itemService.delete(article.Item)
            return True
        return False

# --------------------------------------------------------------------

@injected
@setup(IArticleTargetTypeService, name='articleTargetTypeService')
class ArticleTargetTypeServiceAlchemy(EntityServiceAlchemy, IArticleTargetTypeService):
    '''
    Implementation for @see: IArticleTargetTypeService
    '''

    def __init__(self):
        '''
        Construct the article target type service.
        '''
        EntityServiceAlchemy.__init__(self, ArticleTargetTypeMapped)

    def getTargetTypes(self, id, offset=None, limit=None, detailed=False):
        '''
        @see: IArticleTargetTypeService.getUsers
        '''

        sql = self.session().query(TargetTypeMapped).join(ArticleTargetTypeMapped)
        sql = sql.filter(ArticleTargetTypeMapped.article == id)

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities

    def getUnassignedTargetTypes(self, id, offset=None, limit=None, detailed=False):
        '''
        @see: IArticleTargetTypeService.getUnassignedTargetTypes
        '''
        sql = self.session().query(TargetTypeMapped)
        sql = sql.filter(not_(TargetTypeMapped.id.in_(self.session().query(ArticleTargetTypeMapped.targetType).filter(ArticleTargetTypeMapped.article == id).subquery())))

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities

    def attachTargetType(self, id, targetKey):
        '''
        @see IArticleTargetTypeService.attachTargetType
        '''
        targetId = self._targetTypeId(targetKey)

        sql = self.session().query(ArticleTargetTypeMapped)
        sql = sql.filter(ArticleTargetTypeMapped.article == id)
        sql = sql.filter(ArticleTargetTypeMapped.targetType == targetId)
        if sql.count() == 1: return

        articleTargetType = ArticleTargetTypeMapped()
        articleTargetType.article = id
        articleTargetType.targetType = targetId

        self.session().add(articleTargetType)
        self.session().flush((articleTargetType,))

    def detachTargetType(self, id, targetKey):
        '''
        @see IArticleTargetTypeService.detachTargetType
        '''
        targetId = self._targetTypeId(targetKey)

        sql = self.session().query(ArticleTargetTypeMapped)
        sql = sql.filter(ArticleTargetTypeMapped.article == id)
        sql = sql.filter(ArticleTargetTypeMapped.targetType == targetId)
        count_del = sql.delete()

        return (0 < count_del)

   # ----------------------------------------------------------------

    def _targetTypeId(self, key):
        '''
        Provides the output target type id that has the provided key.
        '''
        try:
            sql = self.session().query(TargetTypeMapped.id).filter(TargetTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid output target type %(type)s') % dict(type=key),))
