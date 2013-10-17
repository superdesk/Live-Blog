'''
Created on Oct 3, 2013

@package: superdesk post verification
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for post verification status API.
'''

from ..api.status import VerificationStatus
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class VerificationStatusMapped(Base, VerificationStatus):
    '''
    Provides the mapping for PostType.
    '''
    __tablename__ = 'verification_status'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Key = Column('key', String(100), nullable=False, unique=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
