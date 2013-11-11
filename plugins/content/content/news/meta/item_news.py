'''
Created on Nov 8, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the SQL alchemy meta for text item API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from content.news.api.item_news import ItemNews
from content.base.meta.item import ItemMapped
from ally.api.validate import validate, ReadOnly

# --------------------------------------------------------------------

TYPE_NEWS = 'news'
# The news type.

@validate(ReadOnly(ItemNews.Type))
class ItemNewsMapped(ItemMapped, ItemNews):
    '''
    Provides the mapping for ItemNews.
    '''
    __tablename__ = 'content_item_news'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8', extend_existing=True)
    __mapper_args__ = dict(polymorphic_identity=TYPE_NEWS)

    HeadLine = Column('headline', String(1000), nullable=False)
    ContentSet = Column('content_set', String(1024), nullable=False)

    # Non REST model attribute --------------------------------------
    itemId = Column('fk_item_id', ForeignKey(ItemMapped.id, ondelete='CASCADE'), primary_key=True)
