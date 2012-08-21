'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the image persistence API.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import handle
from ally.support.util_io import timestampURI
from ally.support.util_sys import pythonPath
from ..api.image_persist import IImagePersistanceService
from ..core.spec import IThumbnailManager
from ..meta.image_data import ImageDataEntry
from ..meta.meta_data import MetaDataMapped
from superdesk.media_archive.core.impl.meta_service_base import thumbnailFormatFor, metaTypeFor
from superdesk.media_archive.core.spec import IMetaDataHandler
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from genericpath import isdir
from os.path import join, abspath, exists
from os import makedirs, access, W_OK
import subprocess

# --------------------------------------------------------------------

@injected
class ImagePersistanceService(IImagePersistanceService, IMetaDataHandler, SessionSupport):
    '''
    Provides the service that handles the image persistence @see: IImagePersistanceService.
    '''

    base_path = join('workspace', 'media_archive', 'content'); wire.config('base_path', doc='''
    The folder path where the images are queued for processing''')
    format_file_name = '%(id)s.%(file)s'; wire.config('format_file_name', doc='''
    The format for the images file names in the media archive''')

    imageType = 'image'
    # The type for the meta type image
    
    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')
    # Provides the thumbnail referencer

    def __init__(self):
        assert isinstance(self.base_path, str), 'Invalid base directory for images %s' % self.base_path
        assert isinstance(self.format_file_name, str), 'Invalid format file name %s' % self.format_file_name
        assert isinstance(self.imageType, str), 'Invalid meta type for image %s' % self.imageType
        
        SessionSupport.__init__(self)

        if not exists(self.base_path): makedirs(self.base_path)
        if not isdir(self.base_path) or not access(self.base_path, W_OK):
            raise IOError('Unable to access the repository directory %s' % self.base_path)

        self._metaTypeId = None

    # ----------------------------------------------------------------
    def extractNumber(self, line):
        for s in line.split(): 
            if s.isdigit():
                return int(s)
            
    # ----------------------------------------------------------------
    def extractString(self, line):
        str = line.partition('-')[2].strip('\n')
        return str
     
    # ----------------------------------------------------------------
    def extractDateTime(self, line):
        #example:' 2010:11:08 18:33:13'
        dateTimeFormat = ' %Y:%m:%d %H:%M:%S'
        str = line.partition('-')[2].strip('\n')
        return datetime.strptime(str, dateTimeFormat)
      
    # ----------------------------------------------------------------
    def generateIdPath (self, id):
        path = join("{0:03d}".format(id // 1000000000), "{0:03d}".format((id // 1000000) % 1000), "{0:03d}".format((id // 1000) % 1000)) 
        
        return path;  
     
    # ----------------------------------------------------------------
    def process(self, metaDataId, contentPath):
        '''
        @see: IMetaDataHandler.process
        '''
        
        metaDataMapped = self.session().query(MetaDataMapped).filter(MetaDataMapped.Id == metaDataId).one()
        if metaDataMapped.Type.find(self.imageType) == -1:
            return False
        
        jarPath = join('tools', 'media-archive-image', 'metadata_extractor.jar');
        p = subprocess.Popen(['java', '-jar', jarPath, contentPath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert p.wait() == 0
        
        imageDataEntry = ImageDataEntry()   
        imageDataEntry.Id = metaDataId    
        while 1:
            line = p.stdout.readline()
            if not line: break   
            line = str(line, "utf-8")
            
            if line.find('] Image Width -') != -1:
                imageDataEntry.Width = self.extractNumber(line)
            elif line.find('] Image Height -') != -1:
                imageDataEntry.Height = self.extractNumber(line)
            elif line.find('] Date/Time Original -') != -1:
                imageDataEntry.CreationDate = self.extractDateTime(line)
            elif line.find('] Make -') != -1:    
                imageDataEntry.CameraMake = self.extractString(line)
            elif line.find('] Model -') != -1:
                imageDataEntry.CameraModel = self.extractString(line)        
                    
        path = join(self.base_path, self.imageType, self.generateIdPath(metaDataId))
        absPath = abspath(path)
        if not exists(absPath): makedirs(absPath)
        
        fileName = self.format_file_name % {'id': metaDataId, 'file': metaDataMapped.Name}
        metaDataMapped.content = join(path, fileName)                                      
        metaDataMapped.typeId = self._metaTypeId 
        metaDataMapped.thumbnailFormatId = self._thumbnailFormat.id   
        metaDataMapped.IsAvailable = True     
        
        self.thumbnailManager.processThumbnail(self._thumbnailFormat.id, contentPath, metaDataMapped)         
                 
        try:            
            self.session().add(imageDataEntry)
        except SQLAlchemyError as e:
            metaDataMapped.IsAvailable = False 
            handle(e, ImageDataEntry)  
        
        return True
    
    # ----------------------------------------------------------------
    def deploy(self):
        '''
           Deploy 
        '''
        self._thumbnailFormatGeneric = thumbnailFormatFor(self.session(), '%(size)s/image_generic.jpg')
        referenceLast = self.thumbnailManager.timestampThumbnail(self._thumbnailFormatGeneric.id)
        imagePath = join(pythonPath(), 'resources', 'other.jpg')
        if referenceLast is None or referenceLast < timestampURI(imagePath):
            self.thumbnailManager.processThumbnail(self._thumbnailFormatGeneric.id, imagePath)
            
        self._thumbnailFormat = thumbnailFormatFor(self.session(), '%(size)s/%(id)d.jpg')  
        self._metaTypeId = metaTypeFor(self.session(), self.imageType).Id  
        
