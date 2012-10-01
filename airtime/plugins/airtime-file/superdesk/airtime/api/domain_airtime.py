'''
Created on Apr 19, 2012

@package: airtime file
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decorator to be used by the models in the airtime domain.
'''

from ally.api.config import model
from functools import partial

# --------------------------------------------------------------------

DOMAIN = 'Airtime'
modelAirtime = partial(model, domain=DOMAIN)
