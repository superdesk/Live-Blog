'''
Created on Sept 26, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''
from superdesk.api.domain_superdesk import modelSuperDesk
from datetime import datetime
from ally.support.api.entity import Entity, IEntityCRUDService
from ally.api.config import service, call
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelSuperDesk
class Article(Entity):
    '''
    Article model
    '''
    Id = int
    CreatedOn = datetime
    Slug = str

# --------------------------------------------------------------------

@service((Entity, Article))
class IArticleService(IEntityCRUDService):
    '''
    Article model service interface
    '''
    
    @call
    def getArticle(self, articleId:Article.Id) -> Article:
        '''
        '''
    
    @call
    def getAll(self) -> Iter(Article):
        '''
        '''