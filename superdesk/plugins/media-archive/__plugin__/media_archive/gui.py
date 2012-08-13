'''
Created on May 3rd, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Publish the GUI resources.
'''

from ally.container import ioc
from ..gui_core.gui_core import publishGui

# --------------------------------------------------------------------

@ioc.start
def publishJS():
    publishGui('media-archive')
    
    