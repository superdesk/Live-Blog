'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog admin API.
'''

from ..api.blog_admin import Admin
from .blog import BlogMapped
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import Column, ForeignKey
from superdesk.meta.metadata_superdesk import Base
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

class AdminDefinition:
    '''
    Provides the mapping for a BlogAdmin definition.
    '''
    __tablename__ = 'livedesk_admin'
    __table_args__ = dict(mysql_engine='InnoDB')

    Blog = declared_attr(lambda cls: Column('fk_blog_id', ForeignKey(BlogMapped.Id), primary_key=True))
    # Non REST model attribute --------------------------------------
    adminId = declared_attr(lambda cls: Column('fk_user_id', ForeignKey(UserMapped.userId), primary_key=True))
    # Never map over the inherited id

class AdminEntry(Base, AdminDefinition):
    '''
    Provides the mapping for a blog Admin entry.
    '''

class AdminMapped(AdminDefinition, UserMapped, Admin):
    '''
    Provides the mapping for blog Admin.
    '''
    __table_args__ = dict(AdminDefinition.__table_args__, extend_existing=True)
