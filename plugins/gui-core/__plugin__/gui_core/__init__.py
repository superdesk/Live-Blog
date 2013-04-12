'''
Created on Jul 15, 2011

@package: GUI core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the GUI setup files.
'''

from ally.container import ioc

# --------------------------------------------------------------------

NAME = 'GUI core'
GROUP = 'GUI'
VERSION = '1.0'
DESCRIPTION = 'Provides the core for the GUI (Graphical User Interface)'

# --------------------------------------------------------------------

@ioc.config
def publish_gui_resources():
    '''Allow for the publish of the gui resources'''
    return True
