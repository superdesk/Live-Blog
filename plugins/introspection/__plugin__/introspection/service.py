'''
Created on Jan 9, 2012

@package: introspection
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the introspection.
'''

from ..plugin.registry import addService
from ally.container import support

# --------------------------------------------------------------------

API = ('introspection.api.**.I*Service', 'introspection.*.api.**.I*Service')
IMPL = ('introspection.impl.**.*', 'introspection.*.impl.**.*')

support.createEntitySetup(API, *IMPL)
support.listenToEntities(*IMPL, listeners=addService())
support.loadAllEntities(*API)

# --------------------------------------------------------------------
