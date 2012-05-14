'''
Created on May 2, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for post API.
'''

from ..api.post import Post
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, DateTime
from superdesk.meta.metadata_superdesk import Base
from superdesk.user.meta.user import User
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from sqlalchemy.orm.mapper import reconstructor
from superdesk.post.meta.type import PostTypeMapped
from sqlalchemy.orm import relationship, backref

# --------------------------------------------------------------------

class PostMapped(Base, Post):
    '''
    Provides the mapping for Post.
    '''
    __tablename__ = 'post'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Creator = Column('fk_creator_id', ForeignKey(User.Id, ondelete='RESTRICT'), nullable=False)
    Author = Column('fk_author_id', ForeignKey(CollaboratorMapped.Id, ondelete='RESTRICT'))
    Content = Column('content', String(1000), nullable=False)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    PublishedOn = Column('published_on', DateTime)
    UpdatedOn = Column('updated_on', DateTime)
    DeletedOn = Column('deleted_on', DateTime)
    # Non REST model attribute --------------------------------------
    typeId = Column('fk_type_id', ForeignKey(PostTypeMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(PostTypeMapped, backref=backref('parent', uselist=False))

    @reconstructor
    def init_on_load(self):
        self.IsModified = self.PublishedOn is not None
        self.Type = self.type.Key
