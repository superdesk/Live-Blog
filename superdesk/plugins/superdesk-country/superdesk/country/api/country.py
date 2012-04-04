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
from ally.api.type import FrontLanguage, IterPart, List
from superdesk.api import modelSuperDesk

# --------------------------------------------------------------------

@modelSuperDesk(id='Code')
class Country:
    '''    
    Provides the country model.
    '''
    Code = str
    Name = str

    def __init__(self, Code=None, Name=None):
        if Code: self.Code = Code
        if Name: self.Name = Name

# --------------------------------------------------------------------

@query
class QCountry:
    '''
    Provides the country query model.
    '''
    name = AsLike
    code = AsLike

# --------------------------------------------------------------------

@service
class ICountryService:
    '''
    Provides services for country.
    '''

    @call
    def getByCode(self, code:Country.Code, translate:List(FrontLanguage)=None) -> Country:
        '''
        Provides the countries having the specified code.
        '''

    @call
    def getAllAvailable(self, offset:int=None, limit:int=10, q:QCountry=None, \
                        translate:List(FrontLanguage)=None) -> IterPart(Country):
        '''
        Provides all the available countries.
        '''
