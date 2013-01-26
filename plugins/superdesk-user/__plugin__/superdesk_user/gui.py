'''
Created on Feb 2, 2012

@package: superdesk user
@copyright: 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the GUI configuration setup for the node presenter plugin.
'''

from ..gui_action.defaults import menuAction
from ..gui_core.gui_core import publishGui, publishedURI
from ally.container import ioc
from distribution.container import app

# --------------------------------------------------------------------

@app.populate
def publishJS():
    publishGui('superdesk/user')
    
@ioc.before(menuAction)
def setActionScripts():
    menuAction().Script = publishedURI('superdesk/user/scripts/js/menu.js')
    
    
