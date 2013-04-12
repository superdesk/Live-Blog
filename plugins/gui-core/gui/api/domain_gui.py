'''
Created on Jan 14, 2013

@package ally 
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Provides the domain definition.
'''

from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

modelGui = partial(model, domain='GUI')
