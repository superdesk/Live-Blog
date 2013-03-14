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
from content.article.api.article import IArticleService
from content.article.meta.article import ArticleMapped

# --------------------------------------------------------------------

@setup(IArticleService, name='articleService')
class ArticleServiceAlchemy(EntityServiceAlchemy, IArticleService):
    '''
    Implementation for @see: IArticleService
    '''

    def __init__(self):
        '''
        Construct the article service.
        '''
        EntityServiceAlchemy.__init__(self, ArticleMapped)
