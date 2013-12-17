'''
Created on Nov 8, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the mongo engine meta for resource item API.
'''

from mongoengine.fields import StringField
from ally.api.validate import validate, ReadOnly
from content.base.meta.mengine.item import ItemMapped
from content.resource.api.item_resource import ItemResource, TYPE_RESOURCE

# --------------------------------------------------------------------

@validate(ReadOnly(ItemResource.Type))
class ItemResourceMapped(ItemMapped, ItemResource):
    '''
    Provides the mapping for ItemResource.
    '''
    HeadLine = StringField(max_length=1000, required=True)
    ContentSet = StringField(max_length=1024, required=True)
    
    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.Type = TYPE_RESOURCE
