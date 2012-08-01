'''
Created on Aug 25, 2011

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for article type API.
'''

from ..api.article_type import IArticleTypeService, QArticleType
from ..meta.article_type import ArticleType
from .entity import EntityServiceAlchemy

# --------------------------------------------------------------------

class ArticleTypeServiceAlchemy(EntityServiceAlchemy, IArticleTypeService):
    '''
    Implementation for @see: IIssueService
    '''

    def __init__(self): EntityServiceAlchemy.__init__(self, ArticleType, QArticleType)
