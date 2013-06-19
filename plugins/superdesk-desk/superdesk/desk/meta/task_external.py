'''
Created on June 18, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for task external link API.
'''

from ..api.task_external import TaskExternalLink
from ..meta.task import TaskMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Text
from superdesk.meta.metadata_superdesk import Base
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

@validate
class TaskExternalLinkMapped(Base, TaskExternalLink):
    '''
    Provides the mapping for TaskExternalLink.
    '''
    __tablename__ = 'desk_task_external_link'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Task = Column('fk_task_id', ForeignKey(TaskMapped.Id, ondelete='CASCADE'), nullable=False)
    Title = Column('title', String(255), unique=False, nullable=False)
    URL = Column('url', String(1024), unique=False, nullable=False)
    Description = Column('description', Text, nullable=True)
