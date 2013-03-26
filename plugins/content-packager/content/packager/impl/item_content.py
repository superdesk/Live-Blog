'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for content.
'''

from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from content.packager.api.item_content import IItemContentService, QItemContent
from content.packager.meta.item_content import ItemContentMapped

# --------------------------------------------------------------------

@setup(IItemContentService, name='itemContentService')
class ContentServiceAlchemy(EntityServiceAlchemy, IItemContentService):
    '''
    Implementation for @see: IContentService
    '''

    def __init__(self):
        '''
        Construct the item content service.
        '''
        EntityServiceAlchemy.__init__(self, ItemContentMapped, QItemContent)
