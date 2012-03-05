'''
Created on Feb 2, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the GUI configuration setup for the node presenter plugin.
'''

from ally.container import ioc
from ..core_gui.gui_core import publishGui
from ally.internationalization import translator

# --------------------------------------------------------------------

_ = translator(__name__)

# --------------------------------------------------------------------

@ioc.start
def publishJS():
    publishGui('superdesk/person')
    
