'''
Created on May 2, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for post type API.
'''

from ..api.type import PostType
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class PostTypeMapped(Base, PostType):
    '''
    Provides the mapping for PostType.
    '''
    __tablename__ = 'post_type'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Key = Column('key', String(100), nullable=False, unique=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
