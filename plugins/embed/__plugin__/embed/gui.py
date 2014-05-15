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
from ally.support.util_sys import callerGlobals
import os
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.config
def embed_html_files():
    ''' the demo client html file '''
    return ['index.html','right-panel.html']

@ioc.config
def embed_themes_path():
    ''' The path to the themes directory '''
    return 'lib/embed/themes'

@ioc.config
def embed_server_host():
    ''' for embed start file update '''
    return 'localhost:8080'

# --------------------------------------------------------------------

@publish
def publishJS():
    publishGui('embed')

@ioc.after(publishJS)
def updateDemoEmbedFile():
    if not publish_gui_resources(): return  # No publishing is allowed
    moduleName, modulePath = __name__, __file__
    print('-------------------------------------1:', moduleName, modulePath)
    for _k in range(0, moduleName.count('.') + 1):
        modulePath = os.path.dirname(modulePath)
    print('-------------------------------------2:', modulePath)
    path = os.path.join(modulePath, 'node_modules')

    cdmGUI().publishFromDir('lib/embed/scripts/js/node_modules', path)
    bootPath = lib_folder_format() % 'embed/'
    for file in embed_html_files():
        try:        
            with openURI(getGuiPath(file)) as f:
                out = f.read().replace(b'{server_url}', bytes(embed_server_host(), 'utf-8'))
                out = out.replace(b'{gui}', bytes(gui_folder_format(), 'utf-8'));
                out = out.replace(b'{lib_core}', bytes(lib_folder_format() % 'core/', 'utf-8'));
                cdmGUI().publishContent(bootPath + file, BytesIO(out))
        except:
            log.exception('Error publishing demo client file')
        else:
            assert log.debug('Client demo script published: \'%s\'', embed_server_host() + getPublishedLib('embed/' + file)) or True
