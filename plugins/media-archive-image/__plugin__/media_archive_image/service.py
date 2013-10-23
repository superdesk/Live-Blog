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
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.entity
def cdmArchiveImage() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')
