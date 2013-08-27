'''
Created on August 26, 2013

@package: superdesk tag
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for superdesk tag API.
'''

from superdesk.tag.api.tag import Tag
from superdesk.tag.meta.type import TagTypeMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from superdesk.meta.metadata_superdesk import Base
from ally.support.sqlalchemy.mapper import validate
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

# --------------------------------------------------------------------

@validate(exclude=('Type',))
class TagMapped(Base, Tag):
    '''
    Provides the mapping for TagMapped definition.
    '''
    __tablename__ = 'tag'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Key = Column('key', String(255), nullable=False, unique=True)
    Type = association_proxy('type', 'Key')
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    typeId = Column('fk_type_id', ForeignKey(TagTypeMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(TagTypeMapped, uselist=False, lazy='joined')
