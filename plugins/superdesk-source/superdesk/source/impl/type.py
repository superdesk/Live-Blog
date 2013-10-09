'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for source type API.
'''

from ..api.type import ISourceTypeService
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.support.util_service import iterateCollection
from sql_alchemy.impl.entity import EntitySupportAlchemy
from superdesk.source.meta.type import SourceTypeMapped

# --------------------------------------------------------------------

@injected
@setup(ISourceTypeService, name='sourceTypeService')
class SourceTypeServiceAlchemy(EntitySupportAlchemy, ISourceTypeService):
    '''Implementation for @see: ISourceTypeService'''

    def __init__(self):
        '''Construct the source type service.'''
        EntitySupportAlchemy.__init__(self, SourceTypeMapped)

    def getById(self, identifier):
        ''':see: IEntityGetPrototype.getById'''
        return self.session().query(self.Mapped).filter(self.MappedId == identifier).one()

    def getAll(self, **options):
        ''':see: IEntityFindPrototype.getAll'''
        return iterateCollection(self.session().query(self.MappedId).order_by(self.MappedId), **options)
