'''
Created on Apr 17, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for media archive meta info.
'''

from .domain_archive import modelArchive
from .meta_data import MetaData, QMetaData
from ally.api.config import query, call, service
from ally.api.criteria import AsLikeOrdered, AsLike
from ally.api.type import Iter#, Count 
from ally.support.api.entity import Entity, QEntity, IEntityGetCRUDService
from superdesk.language.api.language import LanguageEntity

# --------------------------------------------------------------------

@modelArchive
class MetaInfo(Entity):
    '''
    Provides the meta data information that is provided by the user.
    '''

    MetaData = MetaData
    Language = LanguageEntity
    Title = str
    Keywords = str
    Description = str

# --------------------------------------------------------------------

@query(MetaInfo)
class QMetaInfo(QEntity):
    '''
    The query for he meta info model.
    '''
    title = AsLikeOrdered
    keywords = AsLikeOrdered
    description = AsLike

# --------------------------------------------------------------------

@service((Entity, MetaInfo), (QEntity, QMetaInfo))
class IMetaInfoService(IEntityGetCRUDService):
    '''
    Provides the service methods for the meta info.
    '''

    @call
    def getMetaInfos(self, dataId:MetaData.Id=None, languageId:LanguageEntity.Id=None, offset:int=None, limit:int=10,
                     qi:QMetaInfo=None, qd:QMetaData=None) -> Iter(MetaInfo):
        '''
        Provides the meta info's.
        '''
