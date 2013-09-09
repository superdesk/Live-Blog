'''
Created on August 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog post tag API.
'''

from livedesk.meta.blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from superdesk.meta.metadata_superdesk import Base
from superdesk.post.meta.post import PostMapped
from superdesk.tag.meta.tag import TagMapped

# --------------------------------------------------------------------

class BlogPostTagDB(Base):
    '''
    Provides the mapping for BlogPostTagDB definition.
    '''
    __tablename__ = 'livedesk_blog_post_tag'
    __table_args__ = (UniqueConstraint('fk_blog_id', 'fk_post_id', 'fk_tag_id', name='uix_blog_post_tag'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), nullable=False)
    post = Column('fk_post_id', ForeignKey(PostMapped.Id, ondelete='CASCADE'), nullable=False)
    tag = Column('fk_tag_id', ForeignKey(TagMapped.id, ondelete='RESTRICT'), nullable=False)
