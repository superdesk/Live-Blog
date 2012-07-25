'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for media archive image persistence.
'''

from .image_info import ImageInfo
from ally.api.config import service, call, INSERT
from ally.api.model import Content

# --------------------------------------------------------------------

@service
class IImagePersistanceService:
    '''
    Provides the service that handles the image persistence.
    '''

    @call(method=INSERT, webName='Add')
    def insertAll(self, imageInfo:ImageInfo, image:Content) -> ImageInfo.Id:
        '''
        Inserts the image into the media archive.
        '''
