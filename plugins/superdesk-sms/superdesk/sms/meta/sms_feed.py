'''
Created on April 24, 2013

@package: feed sms
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for sms feed API.
'''

from ..api.sms_feed import SMSFeed
from ..meta.sms_feed_type import SMSFeedTypeMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from superdesk.meta.metadata_superdesk import Base
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

@validate(exclude=('Type',))
class SMSFeedMapped(Base, SMSFeed):
    '''
    Provides the mapping for SMSFeed.
    '''
    __tablename__ = 'feed_sms_feed'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    PhoneNumber = Column('phone_number', String(255), unique=False, nullable=False)
    ReceivedOn = Column('received_on', DateTime, nullable=True)
    MessageText = Column('description', Text, nullable=True)
    Type = association_proxy('type', 'Key')
    # Non REST model attribute ---------------------------------------
    typeId = Column('fk_type_id', ForeignKey(SMSFeedTypeMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(SMSFeedTypeMapped, uselist=False, lazy='joined')

