'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog admin API.
'''

from ..api.blog_admin import Admin
from sqlalchemy.schema import Column, ForeignKey
from superdesk.meta.metadata_superdesk import Base
from .blog import BlogMapped
from superdesk.user.meta.user import User
from sqlalchemy.ext.declarative import declared_attr

# --------------------------------------------------------------------

#TODO: this is just a temporary extending mechanism needs to be done by using join.
class AdminDefinition:
    '''
    Provides the mapping for a BlogAdmin definition.
    '''
    __tablename__ = 'livedesk_admin'
    __table_args__ = dict(mysql_engine='InnoDB')

    Id = declared_attr(lambda cls: Column('fk_user_id', ForeignKey(User.Id), primary_key=True))
    Blog = declared_attr(lambda cls: Column('fk_blog_id', ForeignKey(BlogMapped.Id), primary_key=True))

class AdminEntry(Base, AdminDefinition):
    '''
    Provides the mapping for a BlogAdmin entry.
    '''

class AdminMapped(User, AdminDefinition, Admin):
    '''
    Provides the mapping for BlogAdmin.
    '''
    __table_args__ = dict(extend_existing=True)
