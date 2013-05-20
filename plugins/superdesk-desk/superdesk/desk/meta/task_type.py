'''
Created on May 18, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for desk API.
'''

from ..api.task_type import TaskType
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base
from ally.support.sqlalchemy.mapper import validate
from superdesk.desk.meta.task_status import TaskStatusMapped

# --------------------------------------------------------------------

@validate
class TaskTypeMapped(Base, TaskType):
    '''
    Provides the mapping for TaskType.
    '''
    __tablename__ = 'desk_task_type'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Name = Column('name', String(255), unique=True, nullable=False)

# --------------------------------------------------------------------

class TaskTypeTaskStatusMapped(Base):
    '''
    Provides the connecting of TaskType and TaskStatus.
    '''
    __tablename__ = 'desk_task_type_status'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    taskType = Column('fk_task_type_id', ForeignKey(TaskTypeMapped.Id, ondelete='CASCADE'), nullable=False)
    taskStatus = Column('fk_task_status_id', ForeignKey(TaskStatusMapped.Id, ondelete='CASCADE'), nullable=False)