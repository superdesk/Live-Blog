'''
Created on Aug 2, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for languages.
'''

from ally.api.config import service, call, query
from ally.api.criteria import AsLike
from ally.api.type import Iter, FrontLanguage, IdString
from sql_alchemy.api.entity import Entity, IEntityCRUDService
from superdesk.api import modelSuperDesk

# --------------------------------------------------------------------

@modelSuperDesk
class Language:
    '''    
    Provides the language model.
    '''
    Code = IdString
    Name = str
    Territory = str
    Script = str
    Variant = str
    
    def __init__(self, Code=None, Name=None):
        if Code: self.Code = Code
        if Name: self.Name = Name

@modelSuperDesk(name=Language)
class LanguageEntity(Entity, Language):
    '''    
    Provides the language model.
    '''
    Code = str

# --------------------------------------------------------------------

@query
class QLanguage:
    '''
    Provides the language query model.
    '''
    name = AsLike

# --------------------------------------------------------------------

@service((Entity, LanguageEntity))
class ILanguageService(IEntityCRUDService):
    '''
    Provides services for languages.
    '''
    
    @call
    def getByCode(self, code:Language.Code, translate:Iter(FrontLanguage)=None) -> Language:
        '''
        Provides the language having the specified code.
        '''

    @call(webName='Available')
    def getAllAvailable(self, offset:int=None, limit:int=10, q:QLanguage=None,
                        translate:Iter(FrontLanguage)=None) -> Iter(Language):
        '''
        Provides all the available languages.
        '''
    
    #def getCountAvailable(self) -> Count(Language): pass
   
    @call
    def getById(self, id:LanguageEntity.Id, translate:Iter(FrontLanguage)=None) -> LanguageEntity:
        '''
        Provides the language based on the id.
        '''
    
    @call
    def getAll(self, offset:int=None, limit:int=None, translate:Iter(FrontLanguage)=None) -> Iter(LanguageEntity):
        '''
        Provides all the languages available in the system.
        '''
