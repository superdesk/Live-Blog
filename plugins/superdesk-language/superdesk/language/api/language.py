'''
Created on Aug 2, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for languages.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Locale, List, Iter
from ally.support.api.entity import Entity, IEntityCRUDService
from superdesk.api.domain_superdesk import modelLocalization

# --------------------------------------------------------------------

@modelLocalization(id='Code')
class Language:
    '''    
    Provides the language model.
    '''
    Code = str
    Name = str
    Territory = str
    Script = str
    Variant = str

    def __init__(self, Code=None, Name=None):
        if Code: self.Code = Code
        if Name: self.Name = Name

@modelLocalization(name=Language)
class LanguageEntity(Entity, Language):
    '''    
    Provides the language model.
    '''

# --------------------------------------------------------------------

@query(Language)
class QLanguage:
    '''
    Provides the language query model.
    '''
    name = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, LanguageEntity))
class ILanguageService(IEntityCRUDService):
    '''
    Provides services for languages.
    '''

    @call
    def getByCode(self, code:Language.Code, locales:List(Locale)=()) -> Language:
        '''
        Provides the language having the specified code.
        '''

    @call(webName='Available')
    def getAllAvailable(self, locales:List(Locale)=(), offset:int=None, limit:int=LIMIT_DEFAULT,
                        q:QLanguage=None) -> Iter(Language):
        '''
        Provides all the available languages.
        '''

    @call
    def getById(self, id:LanguageEntity.Id, locales:List(Locale)=()) -> LanguageEntity:
        '''
        Provides the language based on the id.
        '''

    @call
    def getAll(self, locales:List(Locale)=(), offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True) -> Iter(LanguageEntity):
        '''
        Provides all the languages available in the system.
        '''
