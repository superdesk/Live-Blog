'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for desk task API.
'''

from ..api.task_link import TaskLink
from ..meta.task import TaskMapped
from ..meta.task_link_type import TaskLinkTypeMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from superdesk.meta.metadata_superdesk import Base
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

@validate(exclude=('Type',))
class TaskLinkMapped(Base, TaskLink):
    '''
    Provides the mapping for TaskLink.
    '''
    __tablename__ = 'desk_task_link'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Head = Column('fk_head_id', ForeignKey(TaskMapped.Id, ondelete='CASCADE'), nullable=False)
    Tail = Column('fk_tail_id', ForeignKey(TaskMapped.Id, ondelete='CASCADE'), nullable=False)
    Description = Column('description', Text, nullable=True)
    Type = association_proxy('type', 'Key')
    # Non REST model attribute ---------------------------------------
    typeId = Column('fk_type_id', ForeignKey(TaskLinkTypeMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(TaskLinkTypeMapped, uselist=False, lazy='joined')

