''',
Created on Jan 25, 2013

@package: superdesk media archive
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Publish the theme files.
'''

from ..gui_core.gui_core import cdmGUI, publish
from .theme import embed_theme_folder_format, getEmbedThemePath
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def publishThemes(name):
    '''
    Publishes themes files
    '''
    assert isinstance(name, str), 'Invalid name: %s' % name
    log.info('Published themes from \'%s\' to \'%s\'', getEmbedThemePath(), embed_theme_folder_format() % name)
    cdmGUI().publishFromDir(embed_theme_folder_format() % name, getEmbedThemePath())

# --------------------------------------------------------------------

@publish
def publishDefaultThemes():
    publishThemes('embed')
