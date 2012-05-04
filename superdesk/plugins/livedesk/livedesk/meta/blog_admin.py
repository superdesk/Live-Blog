'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog admin API.
'''

from ..api.blog_admin import BlogAdmin
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from superdesk.meta.metadata_superdesk import Base
from .blog import BlogMapped
from superdesk.user.meta.user import User

# --------------------------------------------------------------------

class BlogAdminMapped(Base, BlogAdmin):
    '''
    Provides the mapping for BlogAdmin.
    '''
    __tablename__ = 'livedesk_admin'

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id), nullable=False)
    User = Column('fk_user_id', ForeignKey(User.Id), nullable=False)

    __table_args__ = (
                      UniqueConstraint(Blog, User, name='blog_user_unique'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8')
                      )

