'''
Created on May 26, 2011

@package ally core plugins
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Specifications for plugin APIs.
'''

from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

DOMAIN = 'Devel/'
modelDevel = partial(model, domain=DOMAIN)
