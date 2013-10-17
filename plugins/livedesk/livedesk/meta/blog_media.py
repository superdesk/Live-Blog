'''
Created on May 12, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog media API.
'''

from livedesk.api.blog_media import BlogMedia, BlogMediaType
from livedesk.meta.blog import BlogMapped
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base
from sql_alchemy.support.mapper import validate
from sql_alchemy.support.util_meta import relationshipModel

# --------------------------------------------------------------------

class BlogMediaTypeMapped(Base, BlogMediaType):
    '''
    Provides the mapping for BlogMediaType.
    '''
    __tablename__ = 'livedesk_blog_media_type'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Key = Column('key', String(255), nullable=False, unique=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)

# --------------------------------------------------------------------

@validate(exclude=['Type', 'Rank'])
class BlogMediaMapped(Base, BlogMedia):
    '''
    Provides the mapping for BlogMedia.
    '''
    __tablename__ = 'livedesk_blog_media'
    __table_args__ = (UniqueConstraint('fk_blog_id', 'fk_type_id', 'rank', name='uix_blog_media_type_rank'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), nullable=False)
    MetaInfo = Column('fk_metainfo_id', ForeignKey(MetaInfoMapped.Id, ondelete='RESTRICT'), nullable=False)
    Type = relationshipModel(BlogMediaTypeMapped.id)
    Rank = Column('rank', INTEGER(unsigned=True), nullable=False)
