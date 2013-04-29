'''
Created on April 24, 2013

@package: feed
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Provides the decorator to be used by the models in the feed domain.
'''

from ally.api.config import model
from functools import partial

# --------------------------------------------------------------------

DOMAIN = 'Feed/'
modelFeed = partial(model, domain=DOMAIN)
