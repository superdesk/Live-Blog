'''
Created on Nov 11, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the SQL alchemy meta for text item API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from content.base.meta.item import ItemMapped
from ally.api.validate import validate, ReadOnly
from content.package.api.item_package import ItemPackage

# --------------------------------------------------------------------

TYPE_PACKAGE = 'package'
# The package type.

@validate(ReadOnly(ItemPackage.Type))
class ItemPackageMapped(ItemMapped, ItemPackage):
    '''
    Provides the mapping for ItemPackage.
    '''
    __tablename__ = 'content_item_package'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8', extend_existing=True)
    __mapper_args__ = dict(polymorphic_identity=TYPE_PACKAGE)

    HeadLine = Column('headline', String(1000), nullable=False)

    # Non REST model attribute --------------------------------------
    itemId = Column('fk_item_id', ForeignKey(ItemMapped.id, ondelete='CASCADE'), primary_key=True)
