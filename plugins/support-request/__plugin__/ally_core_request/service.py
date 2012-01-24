'''
Created on Jan 9, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the node presenter plugin.
'''

from __plugin__.plugin.registry import services
from ally.container import ioc, support
from ally_core_request.api.request_introspection import \
    IRequestIntrospectService
from ally_core_request.impl.request_introspection import \
    RequestIntrospectService
from ally.core.spec.resources import ConverterPath
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

support.createEntitySetup('ally_core_request.api.**.I*Service', 'ally_core_request.impl.*.*Service')

# --------------------------------------------------------------------

@ioc.entity
def converterPath() -> ConverterPath:
    try: 
        import ally_deploy_application
        return support.entityFor(ConverterPath, ally_deploy_application.assembly)
    except:
        log.exception('No converter path available in the application')
        return ConverterPath()

@ioc.entity
def requestIntrospectService() -> IRequestIntrospectService: return RequestIntrospectService()

@ioc.before(services)
def registerService(): services().append(requestIntrospectService())
