'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog collaborator API.
'''

from ..api.blog_collaborator import BlogCollaborator
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from superdesk.meta.metadata_superdesk import Base
from .blog import BlogMapped
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from sqlalchemy.ext.declarative import declared_attr

# --------------------------------------------------------------------

class BlogCollaboratorDefinition:
    '''
    Provides the mapping for BlogCollaborator definition.
    '''
    __tablename__ = 'livedesk_collaborator'
    __table_args__ = dict(mysql_engine='InnoDB')

    Blog = declared_attr(lambda cls: Column('fk_blog_id', ForeignKey(BlogMapped.Id), primary_key=True))

    # Non REST model attribute --------------------------------------
    blogCollaboratorId = declared_attr(lambda cls: Column('fk_collaborator_id',
                                                          ForeignKey(CollaboratorMapped.Id), primary_key=True))
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
