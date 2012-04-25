'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the image persistence API.
'''

from ally.container.ioc import injected
from superdesk.media_archive.api.image_persist import IImagePersistanceService

# --------------------------------------------------------------------

@injected
class ImagePersistanceService(IImagePersistanceService):
    '''
    Provides the service that handles the @see: IImagePersistanceService.
    '''

    def insert(self, metaInfo, image):
        '''
        @see: IImagePersistanceService.insert
        '''
        #TODO: remove
        print(metaInfo)
        print(image)
        return 1
