'''
Created on May 18, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for card (Kanban column) API.
'''


from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Text
from superdesk.meta.metadata_superdesk import Base
from ally.support.sqlalchemy.mapper import validate
from ally.container.binder_op import validateManaged
from superdesk.desk.meta.task_status import TaskStatusMapped
from superdesk.desk.meta.desk import DeskMapped
from superdesk.desk.api.card import Card

# --------------------------------------------------------------------

@validate(exclude=('Order',))
class CardMapped(Base, Card):
    '''
    Provides the mapping for Card.
    '''
    __tablename__ = 'desk_card'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Desk = Column('fk_desk_id', ForeignKey(DeskMapped.Id, ondelete='CASCADE'), nullable=False)
    Order = Column('order', INTEGER(unsigned=True), nullable=True)
    Name = Column('name', String(255), unique=True, nullable=False)
    Description = Column('description', Text, nullable=True)
    UpperLimit = Column('upper_limit', INTEGER(unsigned=True), nullable=True)
    Color = Column('color', String(255), nullable=False)

validateManaged(CardMapped.Order)

# --------------------------------------------------------------------

class CardTaskStatusMapped(Base):
    '''
    Provides the connecting of TaskType and TaskStatus.
    '''
    __tablename__ = 'desk_card_status'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    card = Column('fk_card_id', ForeignKey(CardMapped.Id, ondelete='CASCADE'), nullable=False)
    taskStatus = Column('fk_task_status_id', ForeignKey(TaskStatusMapped.id, ondelete='CASCADE'), nullable=False)
