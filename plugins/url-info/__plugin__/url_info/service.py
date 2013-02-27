'''
Created on Dec 20, 2012

@package: url_info
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services for URL info extraction.
'''

from ally.container import support
from ..plugin.registry import registerService

# --------------------------------------------------------------------

SERVICES = 'url_info.api.*.I*Service'

support.createEntitySetup('url_info.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------
