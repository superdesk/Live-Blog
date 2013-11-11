'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content item.
'''

from ally.api.config import service, query
from datetime import datetime
from ally.support.api.entity import IEntityPrototype
from ally.api.criteria import AsRangeIntOrdered, AsDateTimeOrdered
from content.base.api.domain_content import modelContent

# --------------------------------------------------------------------

@modelContent(id='GUID')
class Item:
    '''
    Provides the item model.
    '''
    GUID = str
    Version = int
    CreatedOn = datetime
    VersionOn = datetime
    Type = str

# --------------------------------------------------------------------

@query(Item)
class QItem:
    '''
    Provides the query for active item model.
    '''
    version = AsRangeIntOrdered
    createdOn = AsDateTimeOrdered
    versionOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service(('Entity', Item), ('QEntity', QItem))
class IItemService(IEntityPrototype):
    '''
    Provides the service methods for the items.
    '''
