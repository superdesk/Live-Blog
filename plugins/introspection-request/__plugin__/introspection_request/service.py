'''
Created on Jan 9, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the node presenter plugin.
'''

from ally.container import ioc, support
from ally.core.spec.resources import ConverterPath
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.entity
def converterPath() -> ConverterPath:
    try: 
        import ally_deploy_application
        return support.entityFor(ConverterPath, ally_deploy_application.assembly)
    except:
        log.info('No converter path available in the application', exc_info=True)
        return ConverterPath()

