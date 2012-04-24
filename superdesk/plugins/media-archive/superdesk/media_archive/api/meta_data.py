'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for media archive meta data.
'''

from .domain_archive import modelArchive
from .meta_type import MetaType
from ally.api.config import query, service, call
from ally.api.criteria import AsDateTimeOrdered
from ally.api.type import Reference, Iter, Count
from ally.support.api.entity import Entity, QEntity, IEntityGetService
from datetime import datetime

# --------------------------------------------------------------------

@modelArchive
class MetaData(Entity):
    '''
    Provides the meta data that is extracted based on the content.
    '''
    Type = MetaType
    Content = Reference
    Thumbnail = Reference
    SizeInBytes = int
    CreatedOn = datetime

# --------------------------------------------------------------------

@query
class QMetaData(QEntity):
    '''
    The query for he meta models.
    '''
    createdOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service((Entity, MetaData))
class IMetaDataService(IEntityGetService):
    '''
    Provides the service methods for the meta data.
    '''

    def getMetaDatasCount(self, typeId:MetaType.Id=None, q:QMetaData=None) -> Count:
        '''
        Provides the meta data's count.
        '''

    @call(countMethod=getMetaDatasCount)
    def getMetaDatas(self, typeId:MetaType.Id=None, offset:int=None, limit:int=10, q:QMetaData=None) -> Iter(MetaData):
        '''
        Provides the meta data's.
        '''
