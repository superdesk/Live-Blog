'''
Created on Feb 11, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for blog collaborator group API.
'''

from .blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import DateTime
from superdesk.meta.metadata_superdesk import Base
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped
from livedesk.api.blog_collaborator_group import BlogCollaboratorGroupMember,\
    BlogCollaboratorGroup

# --------------------------------------------------------------------

class BlogCollaboratorGroupMapped(Base, BlogCollaboratorGroup):
    '''
    Provides the mapping for BlogCollaboratorGroup definition.
    '''
    __tablename__ = 'livedesk_collaborator_group'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')
    
    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), nullable=False)
    LastAccessOn = Column('last_access_on', DateTime, nullable=False)

# --------------------------------------------------------------------

class BlogCollaboratorGroupMemberMapped(Base, BlogCollaboratorGroupMember):
    '''
    Provides the mapping for BlogCollaboratorGroupMember definition.
    '''
    __tablename__ = 'livedesk_collaborator_group_member'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')
    
    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Group = Column('fk_group_id', ForeignKey(BlogCollaboratorGroupMapped.Id, ondelete='CASCADE'), nullable=False)
    BlogCollaborator = Column('fk_collaborator_id', ForeignKey(BlogCollaboratorMapped.Id, ondelete='CASCADE'), nullable=False)
    