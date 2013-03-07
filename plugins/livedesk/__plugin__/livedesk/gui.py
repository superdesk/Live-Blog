'''
Created on May 3rd, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Publish GUI files.
'''

from ..gui_core.gui_core import publishGui, publish

# --------------------------------------------------------------------

@publish
def publishJS():
    publishGui('livedesk')
    
    
