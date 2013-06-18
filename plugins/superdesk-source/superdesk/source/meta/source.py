'''
Created on May 2, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for source API.
'''

from ..api.source import Source
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Boolean
from superdesk.meta.metadata_superdesk import Base
from superdesk.source.meta.type import SourceTypeMapped
from sqlalchemy.ext.associationproxy import association_proxy
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

@validate(exclude=['Type'])
class SourceMapped(Base, Source):
    '''
    Provides the mapping for Source.
    '''
    __tablename__ = 'source'
    __table_args__ = (UniqueConstraint('name', 'fk_type_id', name='uix_source_type_name'), dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Type = association_proxy('type', 'Key')
    Name = Column('name', String(255), nullable=False)
    URI = Column('uri', String(255), nullable=False)
    Key = Column('key', String(1024), nullable=True)
    IsModifiable = Column('modifiable', Boolean, nullable=False)
    OriginName = Column('origin_name', String(255), nullable=True)
    OriginURI = Column('origin_uri', String(255), nullable=True)
    # Non REST model attribute --------------------------------------
    typeId = Column('fk_type_id', ForeignKey(SourceTypeMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(SourceTypeMapped, uselist=False, lazy='joined')

