'''
Created on Nov 8, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the SQL alchemy meta for resource item API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from content.base.meta.item import ItemMapped
from content.resource.api.item_resource import ItemResource, TYPE_RESOURCE

# --------------------------------------------------------------------

CATEGORY_RESOURCE = TYPE_RESOURCE
# The resource category.

class ItemResourceMapped(ItemMapped, ItemResource):
    '''
    Provides the mapping for ItemResource.
    '''
    __tablename__ = 'item_resource'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8', extend_existing=True)
    __mapper_args__ = dict(polymorphic_identity=CATEGORY_RESOURCE)

    HeadLine = Column('headline', String(1000), nullable=False)
    ContentSet = Column('content_set', String(1024), nullable=False)
    Class = Column('class', String(100), nullable=False)

    # Non REST model attribute --------------------------------------
    itemId = Column('fk_item_id', ForeignKey(ItemMapped.id, ondelete='CASCADE'), primary_key=True)
