'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

Contains SQL alchemy meta for group API.
'''

from ally.support.sqlalchemy.mapper import validate
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from content.packager.api.item_group import ItemGroup
from content.packager.meta.item import ItemMapped
from sqlalchemy.dialects.mysql.base import INTEGER

# --------------------------------------------------------------------

@validate
class ItemGroupMapped(Base, ItemGroup):
    '''
    Provides the mapping for ItemGroup.
    '''
    __tablename__ = 'item_group'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Item = Column('fk_item_id', ForeignKey(ItemMapped.GUId, ondelete='CASCADE'), nullable=False)
    LocalId = Column('local_id', String(100), nullable=False)
    Role = Column('role', String(255))
    Mode = Column('mode', String(255))
