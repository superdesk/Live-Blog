'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta type API. 
'''

from ..api.meta_type import IMetaTypeService
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from superdesk.media_archive.meta.meta_type import MetaTypeMapped
from sqlalchemy.orm.exc import NoResultFound
from ally.exception import InputError, Ref
from ally.support.sqlalchemy.util_service import buildLimits

# --------------------------------------------------------------------

@injected
@setup(IMetaTypeService, name='metaTypeService')
class MetaTypeServiceAlchemy(SessionSupport, IMetaTypeService):
    '''
    Implementation based on SQL alchemy for @see: IMetaTypeService
    '''

    def __init__(self):
        '''
        Construct the service.
        '''

    def getById(self, id):
        '''
        @see: IMetaTypeService.getById
        '''
        try:
            return self.session().query(MetaTypeMapped).filter(MetaTypeMapped.Id == id).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown meta type id'), ref=MetaTypeMapped.Id))

    def getMetaTypes(self, offset=None, limit=None):
        '''
        @see: IMetaTypeService.getByKey
        '''
        return buildLimits(self.session().query(MetaTypeMapped), offset, limit).all()
