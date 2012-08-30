'''
Created on Aug 25, 2011

@package ally core
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for article type API.
'''

from ..api.article_type import ArticleType, IArticleTypeService
from .entity import EntityService

# --------------------------------------------------------------------

class ArticleTypeService(EntityService, IArticleTypeService):
    '''
    Implementation for @see: IIssueService
    '''
    
    def __init__(self): EntityService.__init__(self, ArticleType)
