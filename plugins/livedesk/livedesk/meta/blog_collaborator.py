'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog collaborator API.
'''

from ..api.blog_collaborator import BlogCollaborator, BlogCollaboratorType
from .blog import BlogMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class BlogCollaboratorTypeMapped(Base, BlogCollaboratorType):
    '''
    Provides the mapping for BlogCollaboratorType definition.
    '''
    __tablename__ = 'livedesk_collaborator_type'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')
    
    Name = Column('name', String(190), nullable=False, unique=True)
    
    # Non REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)

# --------------------------------------------------------------------

class BlogCollaboratorDefinition:
    '''
    Provides the mapping for BlogCollaborator definition.
    '''
    __tablename__ = 'livedesk_collaborator'
    __table_args__ = dict(mysql_engine='InnoDB')

    Blog = declared_attr(lambda cls: Column('fk_blog_id', ForeignKey(BlogMapped.Id), nullable=False, primary_key=True))

    # Non REST model attribute --------------------------------------
    blogCollaboratorId = declared_attr(lambda cls: Column('fk_collaborator_id',
                                                          ForeignKey(CollaboratorMapped.Id), nullable=False, primary_key=True))
    typeId = declared_attr(lambda cls: Column('fk_collaborator_type_id', ForeignKey(BlogCollaboratorTypeMapped.id),
                                              nullable=False, primary_key=True))
    # Never map over the inherited id

class BlogCollaboratorEntry(Base, BlogCollaboratorDefinition):
    '''
    Provides the mapping for BlogCollaborator entry.
    '''

# @validate(exclude=('Type',)) #TODO: cehck why this breaks.
class BlogCollaboratorMapped(BlogCollaboratorDefinition, CollaboratorMapped, BlogCollaborator):
    '''
    Provides the mapping for BlogCollaborator.
    '''
    __table_args__ = (UniqueConstraint('fk_blog_id', 'fk_collaborator_id', name='uix_1'),
                      dict(BlogCollaboratorDefinition.__table_args__, extend_existing=True))
    
    Type = association_proxy('type', 'Name')
    
    # Non REST model attribute --------------------------------------
    type = relationship(BlogCollaboratorTypeMapped, uselist=False, lazy='joined')

# validateManaged(BlogCollaboratorMapped.Type)
