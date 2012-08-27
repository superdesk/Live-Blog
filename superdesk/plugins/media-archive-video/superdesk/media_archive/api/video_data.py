'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for media meta data video archive.
'''

from .domain_archive import modelArchive
from .meta_data import MetaData, QMetaData, IMetaDataService
from ally.api.config import query, service
from ally.api.criteria import AsEqualOrdered

# --------------------------------------------------------------------

@modelArchive
class VideoData(MetaData):
    '''
    Provides the meta data that is extracted based on the content.
    '''
    Width = int

# --------------------------------------------------------------------

@query
class QVideoData(QMetaData):
    '''
    The query for video model.
    '''
    width = AsEqualOrdered

# --------------------------------------------------------------------

@service((MetaData, VideoData), (QMetaData, QVideoData))
class IVideoDataService(IMetaDataService):
    '''
    Provides the service methods for the meta data video.
    '''