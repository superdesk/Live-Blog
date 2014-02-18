'''
Created on Feb 5, 2014

@package: livedesk
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API implementation for liveblog seo.
'''
from livedesk.api.blog_seo import BlogSeo
from livedesk.meta.blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.types import String, Boolean
from superdesk.meta.metadata_superdesk import Base
from livedesk.meta.blog_theme import BlogThemeMapped


# --------------------------------------------------------------------
class BlogSeoMapped(Base, BlogSeo):
    '''
    Provides the mapping for BlogSeo definition.
    '''
    __tablename__ = 'livedesk_blog_seo'

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id), nullable=False)
    BlogTheme = Column('fk_theme_id', ForeignKey(BlogThemeMapped.Id), nullable=False)
    RefreshActiv = Column('refresh_activ', Boolean, nullable=False)
    RefreshInterval = Column('refresh_interval', INTEGER, nullable=False)
    CallbackActiv = Column('callback_activ', Boolean, nullable=False)
    CallbackURL = Column('callback_url', String(512), nullable=True)
    CId = Column('id_change', INTEGER(unsigned=True))
    NextSync = Column('next_sync', DateTime)
    LastBlocked = Column('last_blocked', DateTime)
    
