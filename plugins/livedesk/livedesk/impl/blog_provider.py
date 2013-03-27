'''
Created on Mar 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the implementation of the blog provider API.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from livedesk.api.blog_provider import IBlogProviderService, QBlogProvider
from livedesk.meta.blog_provider import BlogProviderMapped
from sql_alchemy.impl.entity import EntityServiceAlchemy
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IBlogProviderService, name='blogProviderService')
class BlogProviderServiceAlchemy(EntityServiceAlchemy, IBlogProviderService):
    '''
    Implementation for @see: IBlogProviderService
    '''

    def __init__(self):
        '''
        Construct the blog provider service.
        '''
        EntityServiceAlchemy.__init__(self, BlogProviderMapped, QBlogProvider)
