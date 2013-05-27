'''
Created on Mar 11, 2013

@package: content newsml
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for content newsml.
'''

from ..plugin.registry import registerService
from ally.container import support, ioc
from ally.cdm.spec import ICDM
from ally.cdm.support import ExtendPathCDM
from ..cdm import contentDeliveryManager

# --------------------------------------------------------------------

SERVICES = 'content.newsml.api.**.I*Service'
support.createEntitySetup('content.newsml.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

@ioc.entity
def cdmNewsML() -> ICDM:
    '''
    The content delivery manager (CDM) for the NewsML files.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'export/NewsML/%s')
