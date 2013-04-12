'''
Created on Nov 14, 2012

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decorator to be used by the models in the filters domain.
'''

from ally.api.config import model, alias
from functools import partial

# --------------------------------------------------------------------

DOMAIN = 'Filter/'
modelFilter = partial(model, domain=DOMAIN)
aliasFilter = partial(alias, domain=DOMAIN)
