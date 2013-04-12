'''
Created on Jan 9, 2012

@@package: administration
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the administration support.
'''

from ..plugin.registry import registerService
from ally.container import support

# --------------------------------------------------------------------

SERVICES = 'admin.**.api.**.I*Service'

support.createEntitySetup('admin.**.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService, beforeBinding=False)
support.loadAllEntities(SERVICES)
