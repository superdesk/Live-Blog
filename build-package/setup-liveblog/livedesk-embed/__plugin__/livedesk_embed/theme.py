''',
Created on Jan 25, 2013

@package: superdesk media archive
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Publish the theme files.
'''

from ally.container import ioc
import logging
from ally.support.util_sys import callerGlobals
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.config
def theme_folder_format():
    '''Describes where the theme files are published '''
    return 'lib/%s'

@ioc.config
def themes_path():
    ''' The path to the themes directory '''
    return 'lib/livedesk-embed/themes'

# --------------------------------------------------------------------

def getThemePath(file=None):
    '''Provides the file path within the plugin "gui-themes" directory'''
    gl = callerGlobals(1)
    _moduleName, modulePath = gl['__name__'], gl['__file__']
    path = os.path.join(os.path.dirname(modulePath), 'gui-themes')
    if file: path = os.path.join(path, file.replace('/', os.sep))
    return path
