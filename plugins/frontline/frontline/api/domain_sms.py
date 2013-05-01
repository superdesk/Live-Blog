'''
Created on April 24, 2013

@package: frontline
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Provides the decorator to be used by the models in the frontline domain.
'''

from ally.api.config import model
from functools import partial

# --------------------------------------------------------------------

DOMAIN = 'SMS/'
modelSMS = partial(model, domain=DOMAIN)
