'''
Created on Aug 23, 2012

@package: superdesk media archive video
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services setups for media video archive.
'''

from ..superdesk import service
from ally.container import ioc
from superdesk.media_archive.impl.video_data import VideoDataServiceAlchemy
from cdm.spec import ICDM
from __plugin__.cdm.local_cdm import contentDeliveryManager
from cdm.support import ExtendPathCDM
from superdesk.media_archive.api.video_data import IVideoDataService

# --------------------------------------------------------------------

videoDataHandler = ioc.entityOf('videoDataHandler', service)

@ioc.entity
def cdmArchive() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@ioc.replace(ioc.entityOf(IVideoDataService, service))
def videoData() -> IVideoDataService:
    b = VideoDataServiceAlchemy()
    b.cdmArchive = cdmArchive()
    b.handler = videoDataHandler()
    return b
