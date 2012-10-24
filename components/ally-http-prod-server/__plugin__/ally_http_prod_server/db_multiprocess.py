'''
Created on Oct 18, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Configuration to add multiprocessing abilities to the database.
'''

from __setup__.ally_core_http import server_type
from ally.container import ioc
import ally_deploy_application
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

ioc.activate(ally_deploy_application.assembly)
if server_type() == 'production':
    try:
        from sql_alchemy.multiprocess_config import enableMultiProcessPool
    except ImportError:
        # Probably there is no sql alchemy available.
        log.warning('Cannot enable multiple processors support for database connection pools', exc_info=True)
    else: enableMultiProcessPool()
ioc.deactivate()
