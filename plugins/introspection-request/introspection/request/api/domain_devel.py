'''
Created on Apr 19, 2012

@package: introspection request
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the decorator to be used by the models in the development domain.
'''

from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

DOMAIN = 'Devel/'
modelDevel = partial(model, domain=DOMAIN)
