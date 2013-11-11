'''
Created on Nov 11, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content text item.
'''

from ally.api.config import service, query
from ally.support.api.entity import IEntityPrototype
from ally.api.criteria import AsLikeOrdered
from content.base.api.domain_content import modelContent
from content.base.api.item import Item
from ally.api.type import Reference

# --------------------------------------------------------------------

@modelContent
class ItemPackage(Item):
    '''
    Provides the text item model.
    '''
    HeadLine = str
    ContentSet = Reference

# --------------------------------------------------------------------

@query(ItemPackage)
class QItemPackage:
    '''
    Provides the query for active text item model.
    '''
    headLine = AsLikeOrdered

# --------------------------------------------------------------------

@service(('Entity', ItemPackage), ('QEntity', QItemPackage))
class IItemPackageService(IEntityPrototype):
    '''
    Provides the service methods for the package items.
    '''
