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
from ally.api.model import Content
from ally.api.type import Reference, Iter, Scheme#, Count
from ally.support.api.entity import Entity, QEntity
from datetime import datetime
from superdesk.user.api.user import User
from ally.api.authentication import auth

# --------------------------------------------------------------------

@modelArchive
class MetaData(Entity):
    '''
    Provides the meta data that is extracted based on the content.
    '''
    Name = str
    Type = str
    Content = Reference
    Thumbnail = Reference
    SizeInBytes = int
    Creator = User; Creator = auth(Creator) # This is redundant, is just to keep IDE hinting.
    CreatedOn = datetime

# --------------------------------------------------------------------

@query(MetaData)
class QMetaData(QEntity):
    '''
    The query for he meta models.
    '''
    createdOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service
class IMetaDataService:
    '''
    Provides the service methods for the meta data.
    '''

    @call
    def getById(self, id:MetaData.Id, scheme:Scheme='http', thumbSize:str=None) -> MetaData:
        '''
        Provides the meta data based on the id.
        '''

    @call
    def getMetaDatas(self, scheme:Scheme, typeId:MetaType.Id=None, offset:int=None, limit:int=10, q:QMetaData=None,
                     thumbSize:str=None) -> Iter(MetaData):
        '''
        Provides the meta data's.
        '''


@service
class IMetaDataUploadService(IMetaDataService):
    '''
    Provides the service methods for the meta data.
    '''

    @call(webName='Upload')
    def insert(self, userId:auth(User.Id), content:Content) -> MetaData.Id:
        '''
        Inserts the meta data content into the media archive. The process of a adding a resource to the media archive is as
        follows:
            1. The content is uploaded through this method, automatically the content is identified as to what type of media
            it belongs.
            2. Next the meta info needs to be added to the newly created meta data, the meta info needs to be added based
            on the detected media type.
        '''
