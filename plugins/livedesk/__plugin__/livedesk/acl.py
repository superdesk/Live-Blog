'''
Created on Jan 15, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the acl setup.
'''

from acl.spec import Filter
from ally.container import ioc, support
from superdesk.security.api.filter_authenticated import Authenticated
from livedesk.api.blog import Blog
from livedesk.api.filter_blog import IBlogFilterService

# --------------------------------------------------------------------

@ioc.entity
def filterBlog():
    '''
    Provides filtering for the users blogs.
    '''
    return Filter(1, Authenticated.Id, Blog.Id, support.entityFor(IBlogFilterService))
