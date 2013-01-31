'''
Created on Jan 21, 2013

@package: superdesk media archive
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Creates the model that will be used for multi-plugins queries.
'''

from ally.api.config import query
from ally.api.type import  Reference
from superdesk.user.api.user import User
from superdesk.language.api.language import LanguageEntity
from datetime import datetime
from superdesk.media_archive.api.domain_archive import modelArchive
from superdesk.media_archive.api.criteria import AsIn, \
    AsLikeExpressionOrdered
from sqlalchemy.schema import MetaData
from superdesk.media_archive.api.meta_info import MetaInfo

@modelArchive(id='Id')
class MetaDataInfo(MetaData, MetaInfo):
    '''
    (MetaDataBase, MetaInfoBase)
    Provides the meta data information that is provided by the user.
    '''

    # TODO: if commented below the search return list is not rendered correctly
    Id = int

    MetaDataId = int
    Name = str
    Type = str
    Content = Reference
    Thumbnail = Reference
    SizeInBytes = int
    Creator = User
    CreatedOn = datetime

    Language = LanguageEntity
    Title = str
    Keywords = str
    Description = str

# --------------------------------------------------------------------

@query(MetaDataInfo)
class QMetaDataInfo:
    '''
    The query for the meta data info models for all texts search.
    '''
    all = AsLikeExpressionOrdered
    type = AsIn

# --------------------------------------------------------------------
