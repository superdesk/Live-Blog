'''
Created on Nov 22, 2012

@package: superdesk person icon
@copyright: 2012 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the person icon.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import handle
from sqlalchemy.exc import SQLAlchemyError
from superdesk.media_archive.api.meta_data import IMetaDataService
from superdesk.person_icon.api.person_icon import IPersonIconService
from superdesk.person_icon.meta.person_icon import PersonIconMapped

# --------------------------------------------------------------------

@injected
@setup(IPersonIconService, name='personIconService')
class PersonIconServiceAlchemy(SessionSupport, IPersonIconService):
    '''
    Implementation for @see: IPersonIconService
    '''
    metaDataService = IMetaDataService; wire.entity('metaDataService')
    # provides the metadata service in order to retrieve metadata of the person icon

    def __init__(self):
        '''
        Construct the service
        '''
        assert isinstance(self.metaDataService, IMetaDataService), 'Invalid metadata service %s' % self.metaDataService

    def getByPersonId(self, id, scheme='http', thumbSize=None):
        '''
        @see: IPersonIconService.getById
        '''
        personIcon = self.session().query(PersonIconMapped).get(id)
        if not personIcon: raise InputError(Ref(_('Invalid person icon'), ref=PersonIconMapped.Id))
        assert isinstance(personIcon, PersonIconMapped)
        assert isinstance(self.metaDataService, IMetaDataService)
        metaData = self.metaDataService.getById(personIcon.MetaData, scheme, thumbSize)
        return metaData

    def setIcon(self, personId, metaDataId):
        '''
        @see: IPersonIconService.setIcon
        '''
        entityDb = PersonIconMapped()
        entityDb.Id, entityDb.MetaData = personId, metaDataId
        try:
            self.session().merge(entityDb)
            self.session().flush((entityDb,))
        except SQLAlchemyError as e: handle(e, entityDb)
        return entityDb.Id
