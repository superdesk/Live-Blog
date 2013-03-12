'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for item.
'''

from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from content.packager.api.item import IItemService, Item

# --------------------------------------------------------------------

@setup(IItemService, name='itemService')
class ReferenceServiceAlchemy(EntityServiceAlchemy, IItemService):
    '''
    Implementation for @see: IItemService
    '''

    def getById(self, idref):
        '''
        Implementation for @see: IItemService.getById
        '''
        item = Item()
        return item
