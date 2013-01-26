'''
Created on Mar 23, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ..gui_core.gui_core import publishGui
from distribution.container import app

# --------------------------------------------------------------------

@app.populate
def publishJS():
    publishGui('superdesk/country')
    
    