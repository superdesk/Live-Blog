'''
Created on Dec 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for content package item.
'''

from ally.api.validate import validate
from ally.container.support import setup
from mongo_engine.impl.entity import EntityServiceMongo, EntitySupportMongo
from content.package.api.item_package import IItemPackageService, QItemPackage
from content.package.meta.mengine.item_package import ItemPackageMapped

# --------------------------------------------------------------------

@setup(IItemPackageService, name='itemPackageService')
@validate(ItemPackageMapped)
class ItemPackageServiceMongo(EntityServiceMongo, IItemPackageService):
    '''
    Implementation for @see: IItemResourceService
    '''
    
    def __init__(self):
        '''
        Construct the content item service
        '''
        EntitySupportMongo.__init__(self, ItemPackageMapped, QItemPackage)
