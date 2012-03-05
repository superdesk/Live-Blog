'''
Created on Jul 15, 2011

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Special package that is targeted by the IoC for processing plugins.
'''

from ally.container import ioc
from ally.support.util_sys import callerGlobals
import os
from __plugin__.plugin.registry import cdmGUI
import logging 

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.config
def lib_folder_format():
    ''' describes where the gui libraries are published, used by various plugins '''
    return 'lib/%s'

@ioc.config
def gui_folder_format():
    ''' describes where the gui files are published '''
    return 'gui/%s'


# --------------------------------------------------------------------

def getGuiPath(file=None):
    '''  '''
    gl = callerGlobals()
    moduleName, modulePath = gl['__name__'], gl['__file__']
    for _k in range(0, moduleName.count('.')+1):
        modulePath = os.path.dirname(modulePath)
    path = os.path.join(modulePath, 'gui')
    if file: 
        path = os.path.join(path, file.replace('/', os.sep))
    return path

def publishLib(name):
    ''' 
    Publishes library files based on the GUI directory convention like so:
    gui (main folder)
        scripts
            js
        styles
            css
            less
    relative to the calling plugin
    '''
    assert isinstance(name, str), 'Invalid library name: %s' % name
    log.info('published library %s = %s', lib_folder_format() % name, getGuiPath())
    cdmGUI().publishFromDir(lib_folder_format() % name, getGuiPath())

def getPublishedLib(name):
    '''
    just to keep other modules from using the cdm and settings from this module...
    '''
    return cdmGUI().getURI(lib_folder_format() % name)

def publishGui(name):
    '''
    Publishes a gui file, usually implementation files
    '''
    assert isinstance(name, str), 'Invalid name: %s' % name
    log.info('published gui %s = %s', gui_folder_format() % name, getGuiPath())
    cdmGUI().publishFromDir(gui_folder_format() % name, getGuiPath())

def getPublishedGui(name):
    '''
    just to keep other modules from using the cdm and settings from this module...
    '''
    return cdmGUI().getURI(gui_folder_format() % name)

# --------------------------------------------------------------------