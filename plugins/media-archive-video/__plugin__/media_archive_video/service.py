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
from superdesk.media_archive.api.video_data import IVideoDataService
from superdesk.media_archive.impl.video_data import VideoDataServiceAlchemy

# --------------------------------------------------------------------

videoDataHandler = ioc.getEntity('videoDataHandler', service)

@ioc.replace(ioc.getEntity(IVideoDataService, service))
def videoData() -> IVideoDataService:
    b = VideoDataServiceAlchemy()
    b.handler = videoDataHandler()
    return b
