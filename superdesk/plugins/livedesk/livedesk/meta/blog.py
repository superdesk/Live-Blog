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
from sqlalchemy.schema import Column, ForeignKey
from superdesk.meta.metadata_superdesk import Base
from superdesk.language.meta.language import LanguageEntity
from superdesk.user.meta.user import User
from sqlalchemy.types import String, DateTime, Text

# --------------------------------------------------------------------

class BlogMapped(Base, Blog):
    '''
    Provides the mapping for Blog.
    '''
    __tablename__ = 'livedesk_blog'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Language = Column('fk_language_id', ForeignKey(LanguageEntity.Id), nullable=False)
    Creator = Column('fk_creator_id', ForeignKey(User.Id), nullable=False)
    Title = Column('title', String(255), nullable=False)
    Description = Column('description', Text)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    LiveOn = Column('live_on', DateTime)
    ClosedOn = Column('closed_on', DateTime)
