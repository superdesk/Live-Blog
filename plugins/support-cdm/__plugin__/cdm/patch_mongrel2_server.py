'''
Created on Nov 23, 2011

@package: support cdm
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the Mongrel2 web server plugins patch for the cdm.
'''

from ..cdm import use_linked_cdm
from __setup__.ally_http import server_type
from ally.container import ioc, support

# --------------------------------------------------------------------

ioc.doc(use_linked_cdm, '''
!!!Attention, if the mongrel2 server is selected this option will always be "false"
''')

@ioc.before(use_linked_cdm, auto=False)
def use_linked_cdm_force():
    if server_type() == 'mongrel2': support.force(use_linked_cdm, False)

