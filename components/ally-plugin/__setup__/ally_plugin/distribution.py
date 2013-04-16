'''
Created on Feb 6, 2013

@package: ally plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the distribution controlled events for the plugins.
'''

from ally.container import ioc

# --------------------------------------------------------------------

APP_NORMAL = 'normal'
# Name used for normal application mode.
APP_DEVEL = 'devel'
# Name used for development application mode.

# --------------------------------------------------------------------

@ioc.config
def distribution_file_path():
    ''' The name of the distribution file for the plugins deployments'''
    return 'distribution.properties'

@ioc.config
def application_mode():
    '''
    The distribution application mode, the possible values are:
    "normal" - the application behaves as the normal production instance, this means:
            * the deployments are executed every time, as it should normally would
            * the populates are executed only once as it should normally would
            
    "devel" - the application behaves as a development instance, this means:
            * the deployments are executed every time, as it should normally would
            * the populates are executed only once as it should normally would except those that are marked for development.
    '''
    return APP_DEVEL
