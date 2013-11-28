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
from ally.internationalization import _
from sqlalchemy.exc import OperationalError, IntegrityError
from superdesk.media_archive.api.meta_data import IMetaDataService
from superdesk.person_icon.api.person_icon import IPersonIconService
from sql_alchemy.support.util_service import SessionSupport
from ally.api.error import InputError
from superdesk.person_icon.meta.person_icon import PersonIcon

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
        personIcon = self.session().query(PersonIcon).get(id)
        
        if not personIcon: raise InputError(_('Invalid person icon'), str(id))
        assert isinstance(personIcon, PersonIcon)
        assert isinstance(self.metaDataService, IMetaDataService)
        metaData = self.metaDataService.getById(personIcon.MetaData, scheme, thumbSize)
        return metaData

    def setIcon(self, personId, metaDataId):
        '''
        @see: IPersonIconService.setIcon
        '''
        entityDb = PersonIcon()
        entityDb.Id, entityDb.MetaData = personId, metaDataId
        self.session().merge(entityDb)
        self.session().flush((entityDb,))
        return entityDb.Id

    def detachIcon(self, personIconId):
        '''
        @see: IPersonIconService.detachIcon
        '''
        try:
            return self.session().query(PersonIcon).filter(PersonIcon.id == personIconId).delete() > 0
        except (OperationalError, IntegrityError):
            raise InputError(_('Can not detach person icon because in use'),)
