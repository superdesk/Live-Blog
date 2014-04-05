'''
Created on Jan 20, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Contains the SQL alchemy meta for desk-user-workflow association API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from .metadata_workflow import Base
from workflow.meta.desk import DeskMapped
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

class DeskUserWorkflow(Base):
    '''
    Desk-User-Workflow association.
    '''
    __tablename__ = 'desk_user_workflow'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    desk = Column('fk_desk_id', ForeignKey(DeskMapped.id), nullable=False, primary_key=True)
    user = Column('fk_user_id', ForeignKey(UserMapped.Id), nullable=False, primary_key=True)
    Workflow = Column('workflow', String(250), nullable=False, primary_key=True)
    
    