'''
Created on Nov 11, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content text item.
'''

import logging
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.api.validate import validate
from ally.container.support import setup
from content.package.api.item_package import IItemPackageService, QItemPackage
from content.package.meta.item_package import ItemPackageMapped

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@setup(IItemPackageService, name='itemPackageService')
@validate(ItemPackageMapped)
class ItemServiceAlchemy(EntityServiceAlchemy, IItemPackageService):
    '''
    Implementation for @see: IItemPackageService
    '''
    
    def __init__(self):
        EntityServiceAlchemy.__init__(self, ItemPackageMapped, QItemPackage)
