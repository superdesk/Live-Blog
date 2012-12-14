'''
Created on Sept 26, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''
from sql_alchemy.impl.entity import EntityCRUDServiceAlchemy
from superdesk.article.api.article import IArticleService, Article
from ..meta.article import ArticleMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sqlalchemy.orm.exc import NoResultFound
from ally.exception import InputError, Ref
from ally.internationalization import _

# --------------------------------------------------------------------

@injected
@setup(IArticleService)
class ArticleServiceAlchemy(EntityCRUDServiceAlchemy, IArticleService):
    
    def __init__(self):
        EntityCRUDServiceAlchemy.__init__(self, ArticleMapped)
        
    def getArticle(self, articleId):
        '''
        @see:
        '''
        sql = self.session().query(ArticleMapped)
        sql = sql.filter(ArticleMapped.Id == articleId)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('Unknown id'), ref=Article.Id))

    def getBySlug(self, slug):
        '''
        @see:
        '''
        sql = self.session().query(ArticleMapped)
        sql = sql.filter(ArticleMapped.Slug == slug)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('Unknown id'), ref=Article.Id))

    def getAll(self):
        '''
        @see:
        '''
        sql = self.session().query(ArticleMapped)
        
        return sql.all()
