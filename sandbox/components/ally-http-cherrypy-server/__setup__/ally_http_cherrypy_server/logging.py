'''
Created on Nov 7, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Update the default logging.
'''

from ..ally_core.logging import warning_for
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.before(warning_for)
def updateWarnings():
    return warning_for().append('cherrypy')
