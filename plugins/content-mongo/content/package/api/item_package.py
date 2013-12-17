'''
Created on Dec 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content package item.
'''

from ally.api.config import query, service
from ally.api.criteria import AsLikeOrdered
from content.base.api.domain_content import modelContent
from content.base.api.item import Item, QItem
from ally.support.api.entity import IEntityPrototype
from ally.api.type import List

# --------------------------------------------------------------------

@modelContent(id='GUID')
class Ref:
    '''
    Provides the reference model (reference to item).
    '''
    GUID = str
    ResidRef = str
    Title = str
    Description = str

@modelContent(id='GUID')
class Group:
    '''
    Provides the group model (group of references).
    '''
    GUID = str
    Id = str
    Role = str
    Mode = str
    Title = str
    Refs = List(str)

# --------------------------------------------------------------------

TYPE_PACKAGE = 'package'
# The package type.(value of Item.Type for this item)
CLASS_COMPOSITE = 'composite'
# The text class (the value of ItemResource.ItemClass for this item)

@modelContent(polymorph={Item.Type: TYPE_PACKAGE})
class ItemPackage(Item):
    '''
    Provides the package item model.
    '''
    RootGroup = str
    Groups = List(str)

# --------------------------------------------------------------------

@query(ItemPackage)
class QItemPackage(QItem):
    '''
    Provides the query for active text item model.
    '''
    headLine = AsLikeOrdered

# --------------------------------------------------------------------

@service(('Entity', ItemPackage), ('QEntity', QItemPackage))
class IItemPackageService(IEntityPrototype):
    '''
    Provides the service methods for pacakge items.
    '''
