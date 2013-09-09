'''
Created on August 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog post tag API.
'''

from livedesk.api.blog_post_tag import BlogPostTag
from livedesk.meta.blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from superdesk.meta.metadata_superdesk import Base
from superdesk.post.meta.post import PostMapped
from superdesk.tag.meta.tag import TagMapped
from ally.support.sqlalchemy.mapper import validate
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

# --------------------------------------------------------------------

@validate(exclude=('Type',))
class BlogPostTagMapped(Base, BlogPostTag):
    '''
    Provides the mapping for BlogPostTagMapped definition.
    '''
    __tablename__ = 'livedesk_post_tag'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Type = association_proxy('type', 'Key')
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), nullable=False)
    Post = Column('fk_post_id', ForeignKey(PostMapped.Id, ondelete='CASCADE'), nullable=False)
    # Non REST model attribute --------------------------------------
    typeId = Column('fk_type_id', ForeignKey(TagMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(TagMapped, uselist=False, lazy='joined')
