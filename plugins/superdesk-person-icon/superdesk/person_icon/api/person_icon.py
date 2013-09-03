'''
Created on Mar 6, 2012

@package: superdesk person icon
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

The API specifications for the person icon.
'''

from ally.api.config import service, call, INSERT, DELETE
from ally.api.type import Scheme
from ally.support.api.entity import Entity
from superdesk.api.domain_superdesk import modelHR
from superdesk.media_archive.api.meta_data import MetaData
from superdesk.person.api.person import Person

# --------------------------------------------------------------------
#TODO: Gabriel: this is wrong, there should not be a person icon.
@modelHR
class PersonIcon(Entity):
    '''
    Provides the icon for a Person from the media archive.
    '''
    Person = Person
    MetaData = MetaData

# --------------------------------------------------------------------

@service
class IPersonIconService:
    '''
    Person icon model service interface
    '''

    @call(webName='Icon')
    def getByPersonId(self, id:Person.Id, scheme:Scheme='http', thumbSize:str=None) -> MetaData:
        '''
        Provides the PersonIcon entity based on the person id.

        @param id: integer
            The id of the person entity to find.
        @raise InputError: If the id is not valid.
        @return: PersonIcon
            Returns the entity identified by the id parameter.
        '''

    @call(method=INSERT) #TODO: Gabriel: this should be just update.
    def setIcon(self, personId:Person.Id, metaDataId:MetaData.Id) -> PersonIcon.Id:
        '''
        Associates the icon referenced by the metadata identifier with the person.

        @param personId: Person.Id
            The identifier of the person
        @param metaDataId: MetaData.Id
            The identifier of the metadata
        @raise InputError: If the any of the identifiers is not valid.
        @return: PersonIcon.Id
            Returns the identifier of the person for which the association took place.
        '''

    @call(method=DELETE)
    def detachIcon(self, personIconId:PersonIcon.Id) -> bool:
        '''
        @param personIconId: PersonIcon.Id
            The identifier of the person icon
        @return: actual removal success
        '''
