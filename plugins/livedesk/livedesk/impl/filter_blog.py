'''
Created on Jan 12, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The implementation for the blog filter.
'''

from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from livedesk.api.filter_blog import IBlogFilterService
from livedesk.meta.blog import BlogMapped
from livedesk.meta.blog_admin import AdminEntry
from sqlalchemy.sql.expression import exists

# --------------------------------------------------------------------

@setup(IBlogFilterService, name='blogFilterService')
class BlogFilterServiceAlchemy(SessionSupport, IBlogFilterService):
    '''
    Implementation for @see: IBlogFilterService
    '''
    
    def isAllowed(self, adminId, blogId):
        '''
        @see: IBlogFilterService.isAllowed
        '''
        sql = self.session().query(BlogMapped).filter((BlogMapped.Creator == adminId) | 
                                                      exists().where((AdminEntry.adminId == adminId) & 
                                                                     (AdminEntry.Blog == BlogMapped.Id)))
        sql = sql.filter(BlogMapped.Id == blogId)
        return sql.count() > 0
        
