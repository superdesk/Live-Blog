'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog post API.
'''

from ..api.blog_post import BlogPost
from livedesk.meta.blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import case
from superdesk.meta.metadata_superdesk import Base
from superdesk.post.meta.post import PostMapped
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from sqlalchemy.types import REAL

# --------------------------------------------------------------------

class BlogPostDefinition:
    '''
    Provides the mapping for BlogCollaborator definition.
    '''
    __tablename__ = 'livedesk_post'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    CId = declared_attr(lambda cls: Column('id_change', INTEGER(unsigned=True)))
    Blog = declared_attr(lambda cls: Column('fk_blog_id', ForeignKey(BlogMapped.Id), nullable=False))
    Order = declared_attr(lambda cls: Column('ordering', REAL))
    # Non REST model attribute --------------------------------------
    blogPostId = declared_attr(lambda cls: Column('fk_post_id', ForeignKey(PostMapped.Id), primary_key=True))
    # Never map over the inherited id

class BlogPostEntry(Base, BlogPostDefinition):
    '''
    Provides the mapping for BlogPost table where it keeps the connection between the post and the blog.
    '''

class BlogPostMapped(BlogPostDefinition, PostMapped, BlogPost):
    '''
    Provides the mapping for BlogPost in the form of extending the Post.
    '''
    __table_args__ = dict(BlogPostDefinition.__table_args__, extend_existing=True)

    @hybrid_property
    def AuthorPerson(self):
        if self.author is None: return self.Creator
        if self.author.User is not None: return self.author.User

    # Expression for hybrid ------------------------------------
    AuthorPerson.expression(lambda cls: case([(cls.author == None, cls.Creator)], else_=
                                             case([(CollaboratorMapped.User != None, CollaboratorMapped.User)])))

