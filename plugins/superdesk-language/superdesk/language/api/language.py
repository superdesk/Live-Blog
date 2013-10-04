'''
Created on Aug 2, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for languages.
'''

from ally.api.config import service, call, query
from ally.api.criteria import AsLikeOrdered
from ally.api.option import SliceAndTotal # @UnusedImport
from ally.api.type import Iter
from ally.support.api.entity import IEntityQueryPrototype, IEntityGetPrototype
from superdesk.api.domain_superdesk import modelLocalization

# --------------------------------------------------------------------

@modelLocalization(id='Code')
class Language:
    ''' Provides the language model.'''
    Code = str
    Name = str
    Territory = str
    Script = str
    Variant = str

    def __init__(self, Code=None, Name=None):
        if Code: self.Code = Code
        if Name: self.Name = Name

# --------------------------------------------------------------------

@query(Language)
class QLanguage:
    '''Provides the language query model.'''
    name = AsLikeOrdered

# --------------------------------------------------------------------

@service(('Entity', Language), ('QEntity', QLanguage))
class ILanguageService(IEntityGetPrototype, IEntityQueryPrototype):
    '''Provides services for languages.'''

    @call(webName='Available')
    def getAllAvailable(self, q:QLanguage=None, **options:SliceAndTotal) -> Iter(Language.Code):
        '''Provides all the available languages.'''
        
    @call
    def add(self, code:Language.Code):
        '''Add the provided language code as a system available language.
        This makes the language available also for other resources.
        '''
        
    @call
    def remove(self, code:Language.Code) -> bool:
        '''Remove the provided language code from the system.'''
