'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog collaborator API.
'''

from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Boolean

from superdesk.meta.metadata_superdesk import Base

from ..api.blog_collaborator import BlogCollaboratorType
from gui.action.meta.category import WithCategoryAction


# --------------------------------------------------------------------
class BlogCollaboratorTypeMapped(Base, BlogCollaboratorType):
    '''
    Provides the mapping for BlogCollaboratorType definition.
    '''
    __tablename__ = 'livedesk_collaborator_type'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')
    
    Name = Column('name', String(190), nullable=False, unique=True)
    IsDefault = Column('is_default', Boolean, nullable=False, default=False)
    # Non REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)

# --------------------------------------------------------------------

class BlogCollaboratorTypeAction(Base, WithCategoryAction):
    '''
    Provides the blog collaborator to Action mapping.
    '''
    __tablename__ = 'livedesk_collaborator_type_action'
    
    categoryId = Column('fk_collaborator_type_id', ForeignKey(BlogCollaboratorTypeMapped.id, ondelete='CASCADE'),
                        primary_key=True)
