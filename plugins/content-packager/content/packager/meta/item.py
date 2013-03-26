'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

Contains SQL alchemy meta for item API.
'''

from ally.support.sqlalchemy.mapper import validate
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime
from content.packager.api.item import Item

# --------------------------------------------------------------------

@validate
class ItemMapped(Base, Item):
    '''
    Provides the mapping for Item.
    '''
    __tablename__ = 'item'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    GUId = Column('guid', String(190), primary_key=True)
    Version = Column('version', Integer(unsigned=True))
    ItemClass = Column('item_class', String(255))
    Urgency = Column('urgency', String(255))
    HeadLine = Column('head_line', String(255))
    SlugLine = Column('slug_line', String(255))
    Byline = Column('byline', String(255))
    CreditLine = Column('credit_line', String(255))
    FirstCreated = Column('first_created', DateTime)
    VersionCreated = Column('version_created', DateTime)
