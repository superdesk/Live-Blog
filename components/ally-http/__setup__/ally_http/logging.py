'''
Created on Nov 7, 2012

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Update the default logging.
'''

from ..ally.logging import info_for
from ally.container import ioc
from ally.http import server

# --------------------------------------------------------------------

@ioc.before(info_for)
def updateInfos():
    return info_for().append(server.__name__)
