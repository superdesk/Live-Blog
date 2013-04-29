'''
Created on April 24, 2013

@package: feed sms
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for sms feed type API.
'''

from ..api.sms_feed_type import SMSFeedType
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Boolean
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class SMSFeedTypeMapped(Base, SMSFeedType):
    '''
    Provides the mapping for SMSFeedType.
    '''
    __tablename__ = 'feed_sms_feed_type'
    __table_args__ = dict(mysql_engine='InnoDB')

    Key = Column('key', String(255), nullable=False, unique=True)
    Active = Column('active', Boolean, nullable=False, default=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)

