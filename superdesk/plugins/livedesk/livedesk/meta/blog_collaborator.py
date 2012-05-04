'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog collaborator API.
'''

from ..api.blog_collaborator import BlogCollaborator
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from superdesk.meta.metadata_superdesk import Base
from .blog import BlogMapped
from superdesk.collaborator.meta.collaborator import CollaboratorMapped

# --------------------------------------------------------------------

class BlogCollaboratorMapped(Base, BlogCollaborator):
    '''
    Provides the mapping for BlogCollaborator.
    '''
    __tablename__ = 'livedesk_collaborator'

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Blog = Column('fk_blog_id', ForeignKey(BlogMapped.Id), nullable=False)
    Collaborator = Column('fk_collaborator_id', ForeignKey(CollaboratorMapped.Id), nullable=False)

    __table_args__ = (
                      UniqueConstraint(Blog, Collaborator, name='blog_collaborator_unique'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8')
                      )
