'''
Created on Aug 23, 2012

@package: superdesk media archive video
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services setups for media video archive.
'''

from ally.container import ioc
from ally.cdm.spec import ICDM
from ally.cdm.support import ExtendPathCDM
from ..cdm.service import contentDeliveryManager

# --------------------------------------------------------------------

@ioc.entity
def cdmArchiveVideo() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

