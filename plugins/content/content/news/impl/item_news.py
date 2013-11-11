'''
Created on Nov 8, 2013

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
from content.news.api.item_news import IItemNewsService, QItemNews
from content.news.meta.item_news import ItemNewsMapped

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@setup(IItemNewsService, name='itemNewsService')
@validate(ItemNewsMapped)
class ItemServiceAlchemy(EntityServiceAlchemy, IItemNewsService):
    '''
    Implementation for @see: IItemNewsService
    '''
    
    def __init__(self):
        EntityServiceAlchemy.__init__(self, ItemNewsMapped, QItemNews)
