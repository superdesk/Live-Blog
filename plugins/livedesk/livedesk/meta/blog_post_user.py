'''
Created on August 28, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog post user API.
'''

from livedesk.api.blog_post_user import BlogPostUser
from livedesk.meta.blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from superdesk.meta.metadata_superdesk import Base
from superdesk.post.meta.post import PostMapped
from superdesk.user.meta.user import UserMapped
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

@validate
class BlogPostUserMapped(Base, BlogPostUser):
    '''
    Provides the mapping for BlogPostUserMapped definition.
    '''
    __tablename__ = 'livedesk_post_user'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), nullable=False)
    Post = Column('fk_post_id', ForeignKey(PostMapped.Id, ondelete='CASCADE'), nullable=False)
    User = Column('fk_user_id', ForeignKey(UserMapped.Id, ondelete='CASCADE'), nullable=False)

#TODO: set unique on blog/post

