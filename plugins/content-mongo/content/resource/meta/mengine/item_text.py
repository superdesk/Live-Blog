'''
Created on Nov 8, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the mongo engine meta for text resource item API.
'''

from ally.api.validate import validate, ReadOnly
from content.resource.api.item_text import ItemText, CLASS_TEXT
from content.resource.meta.mengine.item_resource import ItemResourceMapped

# --------------------------------------------------------------------

@validate(ReadOnly(ItemText.ItemClass))
class ItemTextMapped(ItemResourceMapped, ItemText):
    '''
    Provides the mapping for ItemText.
    '''

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.Class = CLASS_TEXT
