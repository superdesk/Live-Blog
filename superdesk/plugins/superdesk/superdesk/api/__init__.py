'''
Created on Jul 15, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

APIs package.
'''

from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

modelSuperDesk = partial(model, domain='Superdesk/')
