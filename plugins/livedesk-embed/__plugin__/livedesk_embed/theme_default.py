''',
Created on Jan 25, 2013

@package: superdesk media archive
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Publish the theme files.
'''

from __plugin__.livedesk_embed.theme import theme_folder_format, getThemePath
from __plugin__.plugin.registry import cdmGUI
import logging
from ally.container import ioc

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def publishThemes(name):
    '''
    Publishes themes files
    '''
    assert isinstance(name, str), 'Invalid name: %s' % name
    log.info('published themes %s = %s', theme_folder_format() % name, getThemePath())
    cdmGUI().publishFromDir(theme_folder_format() % name, getThemePath())

# --------------------------------------------------------------------

@ioc.start
def publishDefaultThemes():
    publishThemes('livedesk-embed')
