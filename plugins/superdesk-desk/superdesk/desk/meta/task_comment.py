'''
Created on April 23, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for desk task comment API.
'''

from ..api.task_comment import TaskComment
from ..meta.task import TaskMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Text, DateTime
from superdesk.meta.metadata_superdesk import Base
from superdesk.user.meta.user import UserMapped
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

@validate(exclude=('CreatedOn', 'UpdatedOn'))
class TaskCommentMapped(Base, TaskComment):
    '''
    Provides the mapping for TaskComment.
    '''
    __tablename__ = 'desk_task_comment'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Task = Column('fk_task_id', ForeignKey(TaskMapped.Id, ondelete='CASCADE'), nullable=False)
    User = Column('fk_user_id', ForeignKey(UserMapped.Id, ondelete='SET NULL'), nullable=True)
    Text = Column('text', Text, unique=False, nullable=False)
    CreatedOn = Column('created_on', DateTime, nullable=True)
    UpdatedOn = Column('updated_on', DateTime, nullable=True)

