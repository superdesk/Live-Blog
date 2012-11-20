'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

SQL Alchemy based implementation for the video data API. 
'''

from ..api.video_data import QVideoData
from ..meta.video_data import VideoDataMapped
from .meta_data import MetaDataServiceBaseAlchemy
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.core.spec import IMetaDataHandler, IMetaDataReferencer
from superdesk.media_archive.api.video_data import IVideoDataService

# --------------------------------------------------------------------

@injected
@setup(IVideoDataService)
class VideoDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IVideoDataService):
    '''
    @see: IVideoDataService
    '''

    handler = IMetaDataHandler

    def __init__(self):
        assert isinstance(self.handler, IMetaDataHandler), \
        'Invalid handler %s' % self.handler
        MetaDataServiceBaseAlchemy.__init__(self, VideoDataMapped, QVideoData, self)
    
    # ----------------------------------------------------------------

    def populate(self, metaData, scheme, thumbSize=None):
        
        return metaData
