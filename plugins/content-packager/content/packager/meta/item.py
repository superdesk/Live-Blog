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
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, DateTime
from content.packager.api.item import Item
from superdesk.user.meta.user import UserMapped
from superdesk.person.meta.person import PersonMapped

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
    HeadLine = Column('head_line', String(1000))
    Creator = Column('fk_creator_id', ForeignKey(UserMapped.Id, ondelete='RESTRICT'), nullable=False)
    Author = Column('fk_author_id', ForeignKey(PersonMapped.Id, ondelete='RESTRICT'), nullable=False)
    FirstCreated = Column('first_created', DateTime)
    VersionCreated = Column('version_created', DateTime)
    PublishedOn = Column('published_on', DateTime)
