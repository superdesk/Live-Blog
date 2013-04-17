'''
Created on April 15, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for source link type API.
'''

from ..api.task_link_type import TaskLinkType
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Boolean
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class TaskLinkTypeMapped(Base, TaskLinkType):
    '''
    Provides the mapping for TaskLinkType.
    '''
    __tablename__ = 'desk_task_link_type'
    __table_args__ = dict(mysql_engine='InnoDB')

    Key = Column('key', String(255), nullable=False, unique=True)
    IsOn = Column('is_on', Boolean, nullable=False, default=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)

