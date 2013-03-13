'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

Contains SQL alchemy meta for item API.
'''

from ally.support.sqlalchemy.mapper import validate
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, DateTime
from content.packager.api.item import Item, ItemGroup, ItemContent
from sqlalchemy.dialects.mysql.base import INTEGER
from content.packager.meta.group import GroupMapped
from content.packager.meta.content import ContentMapped

# --------------------------------------------------------------------

@validate
class ItemMapped(Base, Item):
    '''
    Provides the mapping for Item.
    '''
    __tablename__ = 'content_item'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    GUId = Column('guid', String(190), primary_key=True)
    Version = Column('version', Integer(unsigned=True))
    ItemClass = Column('item_class', String(255))
    Urgency = Column('urgency', String(255))
    HeadLine = Column('headline', String(255))
    SlugLine = Column('slugline', String(255))
    Byline = Column('byline', String(255))
    CreditLine = Column('creditline', String(255))
    FirstCreated = Column('first_created', DateTime)
    VersionCreated = Column('version_created', DateTime)

# --------------------------------------------------------------------

@validate
class ItemGroupMapped(Base, ItemGroup):
    '''
    Provides the mapping for ItemGroup.
    '''
    __tablename__ = 'content_item_group'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Item = Column('fk_item_id', ForeignKey(ItemMapped.GUId, ondelete='RESTRICT'), nullable=False)
    Group = Column('fk_group_id', ForeignKey(GroupMapped.Id, ondelete='RESTRICT'), nullable=False)

# --------------------------------------------------------------------

@validate
class ItemContentMapped(Base, ItemContent):
    '''
    Provides the mapping for ItemContent.
    '''
    __tablename__ = 'item_content'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Item = Column('fk_item_id', ForeignKey(ItemMapped.GUId, ondelete='RESTRICT'), nullable=False)
    Content = Column('fk_content_id', ForeignKey(ContentMapped.Id, ondelete='RESTRICT'), nullable=False)
