'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for article.
'''

from content.packager.api.domain_content import modelContent
from ally.support.api.entity import Entity, QEntity, IEntityService
from ally.api.config import query, service
from ally.api.criteria import AsLike

# --------------------------------------------------------------------

@modelContent
class Article(Entity):
    '''
    Provides the article model.
    '''
    Creator = str
    Author = str
    Content = str

# --------------------------------------------------------------------

@query(Article)
class QArticle(QEntity):
    '''
    Provides the article query.
    '''
    creator = AsLike
    author = AsLike

# --------------------------------------------------------------------

@service((Entity, Article))
class IArticleService(IEntityService):
    '''
    Provides the service methods for Article model.
    '''
