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
from livedesk.api.blog_type import IBlogTypeService
from sql_alchemy.impl.entity import EntityNQServiceAlchemy, EntitySupportAlchemy
from livedesk.meta.blog_type import BlogTypeMapped
from livedesk.meta.blog_type_post import BlogTypePostMapped
from sqlalchemy.exc import OperationalError
import logging
from superdesk.post.meta.post import PostMapped
from ally.api.error import InputError

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IBlogTypeService, name='blogTypeService')
class BlogTypeServiceAlchemy(EntityNQServiceAlchemy, IBlogTypeService):
    '''
    Implementation for @see: IBlogTypeService
    '''

    def __init__(self):
        '''
        Construct the blog type service.
        '''
        EntitySupportAlchemy.__init__(self, BlogTypeMapped)

    def delete(self, id):
        try:
            postsQ = self.session().query(BlogTypePostMapped.Id).filter(BlogTypePostMapped.BlogType == id)
            posts = [ id for id, in postsQ.all() ]
            if posts:
                self.session().query(PostMapped).filter(PostMapped.Id.in_(posts)).delete(synchronize_session='fetch')
        except OperationalError:
            assert log.debug('Could not delete blog type with id \'%s\'', id, exc_info=True) or True
            raise InputError(_('Cannot delete because is in use'), model=self.model)
        return super().delete(id)
