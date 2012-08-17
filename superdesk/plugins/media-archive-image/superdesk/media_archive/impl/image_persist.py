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
from ..meta.image_data import ImageData
from ..meta.meta_data import MetaDataMapped
from superdesk.media_archive.core.impl.meta_service_base import thumbnailFormatFor, metaTypeFor
from superdesk.media_archive.core.spec import IMetaDataHandler
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from genericpath import isdir
from shutil import copyfile
from os.path import join, abspath, exists
from os import makedirs, access, W_OK
import subprocess

# --------------------------------------------------------------------

@injected
class ImagePersistanceService(IImagePersistanceService, IMetaDataHandler, SessionSupport):
    '''
    Provides the service that handles the @see: IImagePersistanceService.
    '''

    image_dir_path = join('workspace', 'media_archive', 'image_queue'); wire.config('image_dir_path', doc='''
    The folder path where the images are queued for processing''')
    format_file_name = '%(id)s.%(file)s'; wire.config('format_file_name', doc='''
    The format for the images file names in the media archive''')
    default_file_name = 'unknown'; wire.config('default_file_name', doc='''
    The default file name if non is specified''')

    imageType = 'image'
    # The type for the meta type image
    
    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')
    # Provides the thumbnail referencer

    def __init__(self):
        assert isinstance(self.image_dir_path, str), 'Invalid image directory %s' % self.image_dir_path
        assert isinstance(self.format_file_name, str), 'Invalid format file name %s' % self.format_file_name
        assert isinstance(self.default_file_name, str), 'Invalid default file name %s' % self.default_file_name
        assert isinstance(self.imageType, str), 'Invalid meta type for image %s' % self.imageType
        
        SessionSupport.__init__(self)

        if not exists(self.image_dir_path): makedirs(self.image_dir_path)
        if not isdir(self.image_dir_path) or not access(self.image_dir_path, W_OK):
            raise IOError('Unable to access the repository directory %s' % self.image_dir_path)

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

    def process(self, metaData, processingContentPath, contentPath):
        '''
        @see: IMetaDataHandler.process
        '''
        assert isinstance(metaData, MetaDataMapped), 'Invalid meta data %s' % metaData
        if metaData.Type.find(self.imageType) == -1:
            return False
        
        jarPath = join('tools', 'media-archive-image', 'metadata_extractor.jar');
        p = subprocess.Popen(['java', '-jar', jarPath, processingContentPath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert p.wait() == 0
        
        imageData = ImageData()   
        imageData.Id = metaData.Id    
        while 1:
            line = p.stdout.readline()
            if not line: break   
            line = str(line, "utf-8")
            
            if line.find('] Image Width -') != -1:
                imageData.Width = self.extractNumber(line)
            elif line.find('] Image Height -') != -1:
                imageData.Height = self.extractNumber(line)
            elif line.find('] Date/Time Original -') != -1:
                imageData.CreationDate = self.extractDateTime(line)
            elif line.find('] Make -') != -1:    
                imageData.CameraMake = self.extractString(line)
            elif line.find('] Model -') != -1:
                imageData.CameraModel = self.extractString(line)        
                    
        metaData.typeId = self._metaTypeId 
        metaData.thumbnailFormatId = self._thumbnailFormat.id   
        metaData.IsAvailable = True     
                 
        try:            
            self.session().add(imageData)
            self.session().add(metaData)
            self.session().flush((imageData, metaData,))    
        except SQLAlchemyError as e:
            metaData.IsAvailable = False 
            handle(e, imageData)  
            return False  
        
        self.thumbnailManager.processThumbnail(self._thumbnailFormat.id, processingContentPath, metaData)
        
        path = abspath(join(contentPath, self.imageType, self.generateIdPath(metaData.Id)))
        if not exists(path): makedirs(path)
        fileName = self.format_file_name % {'id': metaData.Id, 'file': metaData.Name}
        path = join(path, fileName)
        copyfile(processingContentPath, path)               
        
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
        
