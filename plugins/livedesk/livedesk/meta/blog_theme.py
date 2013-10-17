'''
Created on Aug 30, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the SQL alchemy meta for blog type API.
'''

from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from livedesk.api.blog_theme import BlogTheme
from sql_alchemy.support.mapper import validate

# --------------------------------------------------------------------

@validate
class BlogThemeMapped(Base, BlogTheme):
    '''
    Provides the mapping for BlogTheme.
    '''
    __tablename__ = 'livedesk_blog_theme'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Name = Column('name', String(190), unique=True, nullable=False)
    URL = Column('url', String(1024), nullable=False)
