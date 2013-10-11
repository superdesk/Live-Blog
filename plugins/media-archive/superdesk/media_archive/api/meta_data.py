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
from ally.api.config import query, service, call, model
from ally.api.criteria import AsRangeOrdered, AsDateTimeOrdered
from ally.api.model import Content
from ally.api.type import Reference, Iter, Scheme
from datetime import datetime
from superdesk.media_archive.api.criteria import AsLikeExpressionOrdered, \
    AsInOrdered
from superdesk.user.api.user import User
from ally.support.api.entity_ided import Entity, QEntity

# --------------------------------------------------------------------

@modelArchive
class MetaDataBase:
    '''Provides the meta data that is extracted based on the content.'''
    Name = str
    Type = str
    Content = Reference
    Thumbnail = Reference
    SizeInBytes = int
    Creator = User
    CreatedOn = datetime

# --------------------------------------------------------------------

@model
class MetaData(MetaDataBase, Entity):
    '''Provides the meta data that is extracted based on the content.'''

# --------------------------------------------------------------------

@query(MetaData)
class QMetaData(QEntity):
    '''The query for he meta models.'''
    name = AsLikeExpressionOrdered
    # type = AsInOrdered
    sizeInBytes = AsRangeOrdered
    creator = AsInOrdered
    createdOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service
class IMetaDataService:
    '''Provides the service methods for the meta data.'''

    @call
    def getById(self, id:MetaData.Id, scheme:Scheme='http', thumbSize:str=None) -> MetaData:
        '''Provides the meta data based on the id.'''

    @call
    def getMetaDatas(self, scheme:Scheme, typeId:MetaType.Id=None, q:QMetaData=None,
                     thumbSize:str=None, **options:SliceAndTotal) -> Iter(MetaData.Id):
        '''Provides the meta data's.'''

@service
class IMetaDataUploadService(IMetaDataService):
    '''Provides the service methods for the meta data.'''

    @call(webName='Upload')
    def insert(self, userId:User.Id, content:Content, scheme:Scheme='http', thumbSize:str=None) -> MetaData:
        '''Inserts the meta data content into the media archive. The process of a adding a resource to the media archive is as
        follows:
            1. The content is uploaded through this method, automatically the content is identified as to what type of media
            it belongs.
            2. Next the meta info needs to be added to the newly created meta data, the meta info needs to be added based
            on the detected media type.
        '''
