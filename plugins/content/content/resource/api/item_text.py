'''
Created on Nov 11, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content text item.
'''

from content.base.api.domain_content import modelContent
from content.resource.api.item_resource import ItemResource

# --------------------------------------------------------------------

CLASS_TEXT = 'text'
# The text class (the value of ItemResource.Class for this item)

@modelContent
class ItemText(ItemResource):
    '''
    Provides the text item model.
    '''
    Content = str

# --------------------------------------------------------------------

# no query
