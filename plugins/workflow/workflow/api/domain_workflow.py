'''
Created on Nov 7, 2013

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decorator to be used by the models in the content domain.
'''

from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

DOMAIN = 'WorkFlow/'
modelWorkFlow = partial(model, domain=DOMAIN)
