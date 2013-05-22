'''
Created on May 21, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for output target type API.
'''

from ..api.target_type import TargetType
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class TargetTypeMapped(Base, TargetType):
    '''
    Provides the mapping for TargetType.
    '''
    __tablename__ = 'output_target_type'
    __table_args__ = dict(mysql_engine='InnoDB')

    Key = Column('key', String(255), nullable=False, unique=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)

