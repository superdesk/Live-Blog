'''
Created on Nov 22, 2012

@package: superdesk person icon
@copyright: 2012 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the person icon.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.support.sqlalchemy.util_service import handle
from sqlalchemy.exc import SQLAlchemyError
from ally.support.sqlalchemy.session import SessionSupport
from ally.internationalization import _
from superdesk.person_icon.api.person_icon import IPersonIconService
from superdesk.person_icon.meta.person_icon import PersonIconMapped
from superdesk.person.api.person import Person
from superdesk.media_archive.api.meta_data import MetaData, IMetaDataUploadService
from ally.container import wire

# --------------------------------------------------------------------

@injected
@setup(IPersonIconService)
class PersonIconServiceAlchemy(SessionSupport, IPersonIconService):
    '''
    @see: IPersonIconService
    '''
    metaDataService = IMetaDataUploadService; wire.entity('metaDataService')
    # provides the metadata service in order to retrieve metadata of the person icon

    def __init__(self):
        '''
        Construct the service
        '''
        assert isinstance(self.metaDataService, IMetaDataUploadService), 'Invalid metadata service %s' % self.metaDataService

    def getByPersonId(self, id, scheme='http', thumbSize=None):
        '''
        @see: IPersonIconService.getById
        '''
        personIcon = self.session().query(PersonIconMapped).get(id)
        if not personIcon: raise InputError(Ref(_('Invalid person icon identifier'), ref=PersonIconMapped.Id))
        assert isinstance(personIcon, PersonIconMapped)
        assert isinstance(self.metaDataService, IMetaDataUploadService)
        metaData = self.metaDataService.getById(personIcon.MetaData, scheme, thumbSize)
        return metaData

    def setIcon(self, personId, metaDataId):
        '''
        @see: IPersonIconService.setIcon
        '''
        assert isinstance(personId, Person.Id), 'Invalid person identifier %s' % personId
        assert isinstance(metaDataId, MetaData.Id), 'Invalid metadata identifier %s' % metaDataId
        entityDb = PersonIconMapped()
        entityDb.Person, entityDb.MetaData = personId, metaDataId
        try:
            self.session().add(entityDb)
            self.session().flush((entityDb,))
        except SQLAlchemyError as e: handle(e, entityDb)
        return entityDb.Id

#    def getAll(self, offset=None, limit=None, detailed=False):
#        '''
#        @see: IPersonIconService.getAll
#        '''
#
#    @call
#    def delete(self, ):
#        '''
#        '''
#
#    def update(self,):
#        '''
#        @see: IPersonIconService.update
#        '''
#
#    def delete(self,):
#        '''
#        @see: IPersonIconService.delete
#        '''
