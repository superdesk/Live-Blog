''',
Created on Jan 25, 2013

@package: superdesk media archive
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Publish the theme files.
'''

from ..gui_core.gui_core import cdmGUI, publish
from .theme import theme_folder_format, getThemePath
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def publishThemes(name):
    '''
    Publishes themes files
    '''
    assert isinstance(name, str), 'Invalid name: %s' % name
    log.info('Published themes \'%s\'', theme_folder_format() % name)
    cdmGUI().publishFromDir(theme_folder_format() % name, getThemePath())

# --------------------------------------------------------------------

@publish
def publishDefaultThemes():
    publishThemes('livedesk-embed')
