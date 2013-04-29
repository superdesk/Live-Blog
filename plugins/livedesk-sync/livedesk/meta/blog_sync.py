'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API implementation for liveblog sync.
'''
from sqlalchemy.schema import Column, ForeignKey
from livedesk.meta.blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.types import DateTime, Boolean
from livedesk.api.blog_sync import BlogSync
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class BlogSyncMapped(Base, BlogSync):
    '''
    Provides the mapping for BlogCollaborator definition.
    '''
    __tablename__ = 'livedesk_blog_sync'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id), nullable=False)
    CId = Column('id_change', INTEGER(unsigned=True))
    SyncStart = Column('sync_start', DateTime)
    Auto = Column('auto', Boolean)
