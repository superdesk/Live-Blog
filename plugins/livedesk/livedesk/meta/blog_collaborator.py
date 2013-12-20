'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog collaborator API.
'''

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint

from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.meta.metadata_superdesk import Base

from ..api.blog_collaborator import BlogCollaborator
from .blog import BlogMapped
from .blog_collaborator_type import BlogCollaboratorTypeMapped
from sql_alchemy.support.util_meta import relationshipModel


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

class BlogCollaboratorMapped(BlogCollaboratorDefinition, CollaboratorMapped, BlogCollaborator):
    '''
    Provides the mapping for BlogCollaborator.
    '''
    __table_args__ = (UniqueConstraint('fk_blog_id', 'fk_collaborator_id', name='uix_1'),
                      dict(BlogCollaboratorDefinition.__table_args__, extend_existing=True))
    
    Type = relationshipModel(BlogCollaboratorTypeMapped.id, 'typeId')
