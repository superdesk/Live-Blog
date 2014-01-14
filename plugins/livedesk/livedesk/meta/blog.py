'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog API.
'''

from ..api.blog import Blog
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from superdesk.meta.metadata_superdesk import Base
from superdesk.language.meta.language import LanguageEntity
from superdesk.user.meta.user import UserMapped
from support.api.configuration import Configuration
from support.meta.configuration import ConfigurationDescription
from sqlalchemy.types import String, DateTime, Text
from sqlalchemy.orm import column_property, join
from sqlalchemy.sql.expression import select, func, case
from ally.support.sqlalchemy.mapper import validate
from ally.container.binder_op import validateManaged
from livedesk.meta.blog_type import BlogTypeMapped
from sqlalchemy.ext.hybrid import hybrid_property
from superdesk.source.meta.source import SourceMapped

# --------------------------------------------------------------------

@validate(exclude=('CreatedOn',))
class BlogMapped(Base, Blog):
    '''
    Provides the mapping for Blog.
    '''
    __tablename__ = 'livedesk_blog'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Type = Column('fk_blog_type', ForeignKey(BlogTypeMapped.Id), nullable=False)
    Language = Column('fk_language_id', ForeignKey(LanguageEntity.Id), nullable=False)
    Creator = Column('fk_creator_id', ForeignKey(UserMapped.Id), nullable=False)
    Title = Column('title', String(255), nullable=False)
    Description = Column('description', Text)
    OutputLink = Column('output_link', Text)
    EmbedConfig = Column('embed_config', Text)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    LiveOn = Column('live_on', DateTime)
    ClosedOn = Column('closed_on', DateTime)
    DeletedOn = Column('deleted_on', DateTime)
    @hybrid_property
    def IsLive(self):
        return self.LiveOn is not None and self.ClosedOn is None

    # Expression for hybrid ------------------------------------
    @classmethod
    @IsLive.expression
    def _IsLive(cls):
        return case([((cls.LiveOn != None) & (cls.ClosedOn == None), True)], else_=False)

validateManaged(BlogMapped.CreatedOn)

# --------------------------------------------------------------------

from livedesk.meta.blog_post import PostMapped, BlogPostEntry
BlogMapped.UpdatedOn = column_property(select([func.max(PostMapped.UpdatedOn)]).
                                       select_from(join(PostMapped, BlogPostEntry, PostMapped.Id == BlogPostEntry.blogPostId)).
                                       where(BlogPostEntry.Blog == BlogMapped.Id))

# --------------------------------------------------------------------

class BlogSourceDB(Base):
    '''
    Provides the mapping for BlogSource.
    '''
    __tablename__ = 'livedesk_blog_source'
    __table_args__ = (UniqueConstraint('fk_blog', 'fk_source', name='uix_blog_source'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    blog = Column('fk_blog', ForeignKey(BlogMapped.Id), nullable=False)
    source = Column('fk_source', ForeignKey(SourceMapped.Id, ondelete='RESTRICT'), nullable=False)

# --------------------------------------------------------------------

@validate(exclude=('Name',))
class BlogConfigurationMapped(Base, ConfigurationDescription, Configuration):
    '''
    Provides the mapping for BlogConfiguration.
    '''
    __tablename__ = 'blog_configuration'

    parent = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), primary_key=True)
