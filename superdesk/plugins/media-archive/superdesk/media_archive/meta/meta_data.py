'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media meta data API.
'''

from ..api.meta_data import MetaData
from .meta_type import MetaTypeMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.mapper import reconstructor
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, DateTime, Integer
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class MetaDataMapped(Base, MetaData):
    '''
    Provides the mapping for MetaData.
    '''
    __tablename__ = 'archive_meta_data'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    SizeInBytes = Column('size_in_bytes', Integer)
    CreatedOn = Column('created_on', DateTime)
    # None REST model attribute --------------------------------------
    typeId = Column('type', ForeignKey(MetaTypeMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(MetaTypeMapped, backref=backref('parent', uselist=False))
    reference = Column('reference', String(255))

    @reconstructor
    def init_on_load(self):
        self.Type = self.type.Key
