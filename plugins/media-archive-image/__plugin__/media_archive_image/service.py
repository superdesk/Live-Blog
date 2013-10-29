'''
Created on Aug 23, 2012

@package: superdesk media archive image
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services setups for media image archive.
'''

from ..cdm.service import contentDeliveryManager
from ally.cdm.spec import ICDM
from ally.cdm.support import ExtendPathCDM
from ally.container import ioc, app, support
from ally.container.support import nameInEntity
from ally.container.ioc import entityOf
from superdesk.media_archive.impl.image_persist import ImagePersistanceAlchemy
from os import access, F_OK, R_OK, X_OK
import logging
from ..media_archive.service import detectBinPath

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.entity
def cdmArchiveImage() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@app.dump
def processBinaryRequirements():
    imageMetaProcessorSetup = entityOf(nameInEntity(ImagePersistanceAlchemy, 'metadata_extractor_path'))
    binPath = detectExiv2Path(imageMetaProcessorSetup())
    if binPath is None:
        log.error('Unable to find any binary for image metadata processing')
        return
    if binPath != imageMetaProcessorSetup():
        log.info('Setting image meta processor to %s', binPath)
        support.persist(imageMetaProcessorSetup, binPath)

# --------------------------------------------------------------------

def detectExiv2Path(defaultPath=None):
    if access(defaultPath, F_OK | R_OK | X_OK):
        return defaultPath
    return detectBinPath(('exiv2', 'exiv2.exe'))
