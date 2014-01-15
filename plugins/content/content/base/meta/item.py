'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the SQL alchemy meta for item API.
'''

from sqlalchemy.schema import Column
from sqlalchemy.types import INTEGER, DateTime, String, TIMESTAMP
from sql_alchemy.support.util_meta import UtcNow
from content.base.api.item import Item
from content.base.meta.metadata_content import Base

# --------------------------------------------------------------------

class ItemMapped(Base, Item):
    '''
    Provides the mapping for Item.
    '''
    __tablename__ = 'item'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    GUID = Column('guid', String(255), nullable=False, unique=True)
    Version = Column('version', INTEGER(unsigned=True), nullable=False, default=1)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    VersionOn = Column('version_on', TIMESTAMP, server_default=UtcNow(), nullable=False)
    Type = Column('type', String(255), nullable=False)

    # Non REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    category_ = Column('category_', String(255), nullable=False)

    # mapper arguments ----------------------------------------------
    __mapper_args__ = dict(polymorphic_on=category_, with_polymorphic='*')
