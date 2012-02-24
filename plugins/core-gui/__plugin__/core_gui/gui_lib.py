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
from .gui_core import publishLib
from __plugin__.core_gui.gui_core import getGuiPath, lib_folder_format
from io import BytesIO


# --------------------------------------------------------------------

@ioc.config
def js_core_libs_format():
    ''' The javascript bootstrap relative filename '''
    return 'scripts/js/%s.js'

@ioc.config
def js_core_libs():
    ''' The javascript core libraries '''
    return ['jquery', 'jquery-ui', 'jquery-ui-ext', 'jquery/rest', 'jquery/tmpl', 'startup']

@ioc.config
def js_bootstrap_file():
    ''' The javascript core libraries '''
    return 'startup.js'


@ioc.start
def publish():
    publishLib('core')
    
@ioc.after(publish)
def updateStartup():
    bootPath = lib_folder_format() % 'core/'
    try:
        fileList = [open(getGuiPath(js_core_libs_format() % x), 'r+b') for x in js_core_libs()]
        cdmGUI().publishFromFile(bootPath + js_bootstrap_file(), BytesIO(b'\n'.join([fi.read() for fi in fileList])))
    finally:
        for f in fileList: f.close()
