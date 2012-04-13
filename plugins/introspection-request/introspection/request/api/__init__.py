'''
Created on May 26, 2011

@package: introspection request
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Specifications for the introspection of requests..
'''

from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

DOMAIN = 'Devel/'
modelDevel = partial(model, id='Id', domain=DOMAIN)
