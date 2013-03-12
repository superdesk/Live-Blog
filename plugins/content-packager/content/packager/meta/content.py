'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

Contains SQL alchemy meta for content API.
'''

from ally.support.sqlalchemy.mapper import validate
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.schema import Column
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.types import String, Integer
from content.packager.api.content import Content

# --------------------------------------------------------------------

@validate
class ContentMapped(Base, Content):
    '''
    Provides the mapping for Content.
    '''
    __tablename__ = 'content'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    ContentType = Column('content_type', String(255))
    Content = Column('content', String(10000), nullable=False)
    ResidRef = Column('resid_ref', String(1000))
    Href = Column('href', String(1000))
    Size = Column('size', Integer(unsigned=True))
    Rendition = Column('rendition', String(1000))
