'''
Created on May 22, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides configurations API support blogs.
'''

from livedesk.api.blog import Blog
from support.api.configuration import IConfigurationService
from ally.support.api.entity import Entity
from ally.api.config import service

# --------------------------------------------------------------------

# No Model

# --------------------------------------------------------------------

# No Query

# --------------------------------------------------------------------

@service((Entity, Blog))
class IBlogConfigurationService(IConfigurationService):
    '''
    Provides the blog configuration service.
    '''
