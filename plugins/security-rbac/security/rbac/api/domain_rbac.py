'''
Created on Nov 14, 2012

@package: security RBAC
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides the decorator to be used by the models in the security RBAC domain.
'''

from ally.api.config import model
from functools import partial

# --------------------------------------------------------------------

DOMAIN = 'RBAC/'
modelRbac = partial(model, domain=DOMAIN)