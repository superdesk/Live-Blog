'''
Created on Aug 30, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the implementation of the blog type API.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from livedesk.api.blog_type import IBlogTypeService, QBlogType
from sql_alchemy.impl.entity import EntityServiceAlchemy
from livedesk.meta.blog_type import BlogTypeMapped

# --------------------------------------------------------------------

@injected
@setup(IBlogTypeService)
class BlogTypeServiceAlchemy(EntityServiceAlchemy, IBlogTypeService):
    '''
    Implementation for @see: IBlogTypeService
    '''

    def __init__(self):
        '''
        Construct the blog type service.
        '''
        EntityServiceAlchemy.__init__(self, BlogTypeMapped, QBlogType)
