'''
Created on May 22, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides configurations API support blogs.
'''

from livedesk.api.blog import Blog
from livedesk.api.domain_livedesk import modelLiveDesk
from support.api.configuration import Configuration, QConfiguration, IConfigurationService
from ally.support.api.entity import Entity

# --------------------------------------------------------------------

# No Model

# --------------------------------------------------------------------

# No Query

# --------------------------------------------------------------------

@service((Entity, Blog),)
@service
class IBlogConfigurationService(IConfigurationService):
    '''
    Provides the blog configuration service.
    '''
