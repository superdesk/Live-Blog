''',
Created on May 3rd, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Publish the GUI resources.
'''

from ..gui_core import publish_gui_resources
from ..gui_core.gui_core import getGuiPath, getPublishedLib, gui_folder_format, \
    lib_folder_format, publishGui, publish, cdmGUI
from ally.container import ioc
from ally.support.util_io import openURI
from io import BytesIO
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.config
def ui_demo_embed_files():
    ''' the demo client html file '''
    return ['index.html','right-panel.html']

@ioc.config
def themes_path():
    ''' The path to the themes directory '''
    return 'lib/livedesk-embed/themes'

@ioc.config
def embed_server_url():
    ''' for embed start file update '''
    return 'localhost:8080'

# --------------------------------------------------------------------

@publish
def publishJS():
    publishGui('livedesk-embed')

@ioc.after(publishJS)
def updateDemoEmbedFile():
    if not publish_gui_resources(): return  # No publishing is allowed
    bootPath = lib_folder_format() % 'livedesk-embed/'
    for file in ui_demo_embed_files():
        try:        
            with openURI(getGuiPath(file)) as f:
                out = f.read().replace(b'{server_url}', bytes(embed_server_url(), 'utf-8'))
                out = out.replace(b'{gui}', bytes(gui_folder_format(), 'utf-8'));
                out = out.replace(b'{lib_core}', bytes(lib_folder_format() % 'core/', 'utf-8'));
                cdmGUI().publishContent(bootPath + file, BytesIO(out))
        except:
            log.exception('Error publishing demo client file')
        else:
            assert log.debug('Client demo script published:', embed_server_url() + getPublishedLib('livedesk-embed/' + file)) or True
