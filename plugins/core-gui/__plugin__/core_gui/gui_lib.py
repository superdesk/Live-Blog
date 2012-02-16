'''
Created on Feb 2, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the GUI configuration setup for the node presenter plugin.
'''

from ..plugin.registry import cdmGUI
from ally.container import ioc
from ally.support.util_io import replaceInFile, openURI
from .gui_core import publishLib
from __plugin__.core_gui.gui_core import getGuiPath, lib_folder_format
from __plugin__.plugin.registry import gui_server_url


# --------------------------------------------------------------------

@ioc.config
def js_bootstrap_file():
    ''' The javascript bootstrap relative filename '''
    return 'scripts/js/startup.js'

@ioc.start
def publish():
    publishLib('core')
    
@ioc.after(publish)
def updateStartup():
    bootScript = openURI(getGuiPath(js_bootstrap_file()))
    bootPath = lib_folder_format() % 'core/'+js_bootstrap_file()
    boot = replaceInFile(bootScript, {b'{libUri}': (gui_server_url() + bootPath).encode()})
    
    cdmGUI().publishFromFile(bootPath, boot)