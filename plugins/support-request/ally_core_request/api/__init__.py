'''
Created on May 26, 2011

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Specifications for the node presenter.
'''

from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

DOMAIN = 'Devel/'
model = partial(model, domain=DOMAIN)
