'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for article file.
'''

from content.packager.api.domain_content import modelContent
from ally.support.api.entity import Entity, QEntity, IEntityService
from ally.api.config import query, service
from ally.api.criteria import AsEqual
from content.article.api.article import Article
from superdesk.media_archive.api.meta_data import MetaData

# --------------------------------------------------------------------

@modelContent
class ArticleFile(Entity):
    '''
    Provides the metadata model.
    '''
    Article = Article
    MetaData = MetaData

# --------------------------------------------------------------------

@query(ArticleFile)
class QArticleFile(QEntity):
    '''
    Provides the article file query.
    '''
    article = AsEqual

# --------------------------------------------------------------------

@service((Entity, ArticleFile), (QEntity, QArticleFile))
class IArticleFileService(IEntityService):
    '''
    Provides the service methods for ArticleFile model.
    '''
