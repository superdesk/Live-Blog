'''
Created on August 26, 2013

@package: superdesk tag
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for superdesk tag type API.
'''

from superdesk.tag.api.type import TagType
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.types import String

# --------------------------------------------------------------------

class TagTypeMapped(Base, TagType):
    '''
    Provides the mapping for TagTypeMapped definition.
    '''
    __tablename__ = 'tag_type'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Key = Column('key', String(255), nullable=False, unique=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
