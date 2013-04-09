'''
Created on April 8, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for source type API.
'''

from ..api.task_status import TaskStatus
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Boolean
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class TaskStatusMapped(Base, TaskStatus):
    '''
    Provides the mapping for TaskStatus.
    '''
    __tablename__ = 'desk_task_status'
    __table_args__ = dict(mysql_engine='InnoDB')

    Key = Column('key_label', String(255), nullable=False, unique=True)
    IsOn = Column('is_on', Boolean, nullable=False, default=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)

