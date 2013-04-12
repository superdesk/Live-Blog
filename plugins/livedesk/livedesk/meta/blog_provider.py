'''
Created on Mar 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog provider API.
'''

from ally.support.sqlalchemy.mapper import validate
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Text
from livedesk.api.blog_provider import BlogProvider

# --------------------------------------------------------------------

@validate
class BlogProviderMapped(Base, BlogProvider):
    '''
    Provides the mapping for BlogProvider.
    '''
    __tablename__ = 'livedesk_blog_provider'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Title = Column('title', String(255), unique=True, nullable=False)
    Description = Column('description', Text)
    URL = Column('url', String(1024), nullable=False)
