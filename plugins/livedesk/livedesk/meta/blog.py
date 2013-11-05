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
from superdesk.user.meta.user import UserMapped
from support.api.configuration import Configuration
from support.meta.configuration import WithConfiguration
from sqlalchemy.types import String, DateTime, Text
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import select, func, case
from livedesk.meta.blog_type import BlogTypeMapped
from sqlalchemy.ext.hybrid import hybrid_property
from superdesk.source.meta.source import SourceMapped
from superdesk.language.meta.language import LanguageAvailable
from sql_alchemy.support.util_meta import relationshipModel
from ally.api.validate import validate, ReadOnly

# --------------------------------------------------------------------

@validate(ReadOnly(Blog.CreatedOn))
class BlogMapped(Base, Blog):
    '''
    Provides the mapping for Blog.
    '''
    __tablename__ = 'livedesk_blog'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Type = relationshipModel(BlogTypeMapped.id)
#     Language = Column('fk_language_id', ForeignKey(LanguageAvailable.id), nullable=False)
    Language = relationshipModel(LanguageAvailable.id)
    Creator = Column('fk_creator_id', ForeignKey(UserMapped.Id), nullable=False)
    Title = Column('title', String(255), nullable=False)
    Description = Column('description', Text)
    OutputLink = Column('output_link', Text)
    EmbedConfig = Column('embed_config', Text)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    LiveOn = Column('live_on', DateTime)
    ClosedOn = Column('closed_on', DateTime)
    @hybrid_property
    def IsLive(self):
        return self.LiveOn is not None and self.ClosedOn is None
    # Expression for hybrid ------------------------------------
    @IsLive.expression 
    def _IsLive(cls):  # @NoSelf
        return case([((cls.LiveOn != None) & (cls.ClosedOn == None), True)], else_=False)

# --------------------------------------------------------------------

from livedesk.meta.blog_post import BlogPostMapped
BlogMapped.UpdatedOn = column_property(select([func.max(BlogPostMapped.UpdatedOn)]).
                                       where(BlogPostMapped.Blog == BlogMapped.Id))

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

class BlogConfigurationMapped(Base, WithConfiguration, Configuration):
    '''
    Provides the mapping for BlogConfiguration.
    '''
    __tablename__ = 'blog_configuration'

    targetId = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), primary_key=True)
