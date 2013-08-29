'''
Created on Feb 2, 2012

@package: superdesk person
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the GUI configuration setup for the node presenter plugin.
'''

from ..gui_core.gui_core import publishGui, publish

# --------------------------------------------------------------------

@publish
def publishJS():
    publishGui('superdesk/person')
    
