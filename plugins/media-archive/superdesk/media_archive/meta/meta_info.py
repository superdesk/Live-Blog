'''
Created on Apr 18, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media meta info API.
'''

from ..api.meta_info import MetaInfo
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base
from .meta_data import MetaDataMapped
from sqlalchemy.schema import UniqueConstraint
from superdesk.language.meta.language import LanguageAvailable
from sql_alchemy.support.util_meta import relationshipModel

# --------------------------------------------------------------------

class MetaInfoMapped(Base, MetaInfo):
    '''Provides the mapping for MetaData.'''
    __tablename__ = 'archive_meta_info'

    Id = Column('id', INTEGER(unsigned=True), primary_key=True, key='Id')
    MetaData = relationshipModel(MetaDataMapped.Id)
    Language = relationshipModel(LanguageAvailable.id)
    Title = Column('title', String(255), nullable=True, key='Title')
    Keywords = Column('keywords', String(255), nullable=True, key='Keywords')
    Description = Column('description', String(255), nullable=True, key='Description')

    __table_args__ = (UniqueConstraint(MetaData, Language), dict(mysql_engine='InnoDB', mysql_charset='utf8'))

