'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog post API.
'''

from ..api.blog_post import BlogPost
from .blog import BlogMapped
from sqlalchemy.schema import Column, ForeignKey
from superdesk.post.meta.post import PostMapped

# --------------------------------------------------------------------

class BlogPostMapped(PostMapped, BlogPost):
    '''
    Provides the mapping for BlogPost.
    '''
    __tablename__ = 'livedesk_post'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('fk_post_id', ForeignKey(PostMapped.Id), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id), nullable=False)



