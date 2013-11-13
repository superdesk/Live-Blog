'''
Created on Nov 8, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the SQL alchemy meta for text resource item API.
'''

from sqlalchemy.schema import Column, ForeignKey
from content.resource.api.item_text import ItemText, CLASS_TEXT
from content.resource.meta.item_resource import ItemResourceMapped
from content.resource.api.item_resource import TYPE_RESOURCE
from ally.api.validate import validate, Optional

# --------------------------------------------------------------------

CATEGORY_RESOURCE_TEXT = '%s:%s' % (TYPE_RESOURCE, CLASS_TEXT)
# The text resource category

@validate(Optional(ItemText.ContentSet))
class ItemTextMapped(ItemResourceMapped, ItemText):
    '''
    Provides the mapping for ItemText.
    '''
    __tablename__ = 'item_resource_text'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8', extend_existing=True)
    __mapper_args__ = dict(polymorphic_identity=CATEGORY_RESOURCE_TEXT)

    # Non REST model attribute --------------------------------------
    itemId = Column('fk_item_id', ForeignKey(ItemResourceMapped.itemId, ondelete='CASCADE'), primary_key=True)
