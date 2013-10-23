'''
Created on Oct 22, 2013

@package: frontline-inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API implementation for sms sync.
'''
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from livedesk.meta.blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from superdesk.meta.metadata_superdesk import Base
from superdesk.source.meta.source import SourceMapped
from frontline.inlet.api.sms_sync import SmsSync

# --------------------------------------------------------------------

class SmsSyncMapped(Base, SmsSync):
    '''
    Provides the mapping for SmsSync definition.
    '''
    __tablename__ = 'livedesk_sms_sync'
    __table_args__ = (UniqueConstraint('fk_blog_id', 'fk_source_id', name='uix_sync_sms_source'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id), nullable=False)
    Source = Column('fk_source_id', ForeignKey(SourceMapped.Id), nullable=False)
    LastId = Column('last_id', INTEGER(unsigned=True))
