'''
Created on Jul 15, 2011

@package: superdesk archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

APIs package.
'''

from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

modelArchive = partial(model, domain='Superdesk/Archive/')
