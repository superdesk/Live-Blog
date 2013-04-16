'''
Created on Sep 14, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the time zone conversion processor.
'''

from ..ally_core.processor import conversion
from ..ally_core_http.processor import assemblyResources, \
    updateAssemblyResources
from ally.container import ioc
from ally.design.processor.handler import Handler
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: import pytz
except ImportError: log.info('No pytz library available, no time zone conversion available')
else:
    pytz = pytz  # Just to avoid the import warning
    # ----------------------------------------------------------------

    from ally.core.http.impl.processor.time_zone import TimeZoneHandler
    
    # --------------------------------------------------------------------
    
    @ioc.config
    def base_time_zone():
        '''
        The base time zone that the server date/time values are provided.
        '''
        return 'UTC'
    
    @ioc.config
    def default_time_zone():
        '''
        The default time zone if none is specified.
        '''
        return 'UTC'
    
    # --------------------------------------------------------------------
    
    @ioc.entity
    def timeZone() -> Handler:
        b = TimeZoneHandler()
        b.baseTimeZone = base_time_zone()
        b.defaultTimeZone = default_time_zone()
        return b
    
    # --------------------------------------------------------------------
    
    @ioc.after(updateAssemblyResources)
    def updateAssemblyResourcesForTimeZone():
        assemblyResources().add(timeZone(), after=conversion())
