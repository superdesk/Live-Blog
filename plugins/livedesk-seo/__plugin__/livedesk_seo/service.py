'''
Created on Feb 5, 2014

@package: livedesk
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services for livedesk SEO.
'''

from ally.container import support, ioc
from livedesk.core.impl.seo_sync import SeoSyncProcess
from ally.cdm.spec import ICDM
from __plugin__.cdm import contentDeliveryManager

# --------------------------------------------------------------------
 
support.createEntitySetup(SeoSyncProcess)

# --------------------------------------------------------------------

@ioc.entity
def htmlCDM() -> ICDM: return contentDeliveryManager()

# --------------------------------------------------------------------

