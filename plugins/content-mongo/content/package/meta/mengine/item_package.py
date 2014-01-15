'''
Created on Dec 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the mongo engine meta for package item API.
'''

from mongoengine.fields import ListField, ReferenceField
from ally.api.validate import validate, ReadOnly
from content.base.meta.mengine.item import ItemMapped
from content.package.api.item_package import ItemPackage, TYPE_PACKAGE
from mongoengine.queryset.base import NULLIFY

# --------------------------------------------------------------------

@validate(ReadOnly(ItemPackage.Type))
class ItemPackageMapped(ItemMapped, ItemPackage):
    '''
    Provides the mapping for ItemPackage.
    '''
    Items = ListField(ReferenceField('ItemMapped', reverse_delete_rule=NULLIFY))
    
    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.Type = TYPE_PACKAGE
