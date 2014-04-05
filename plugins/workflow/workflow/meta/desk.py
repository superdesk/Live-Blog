'''
Created on Jan 9, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Contains the SQL alchemy meta for desk API.

'''
from ..api.desk import Desk

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from sqlalchemy.dialects.mysql.base import INTEGER
from .metadata_workflow import Base

# --------------------------------------------------------------------

class DeskMapped(Base, Desk):
    '''
    Provides the mapping for Desk entity.
    '''
    __tablename__ = 'workflow_desk'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    
    Name = Column('name', String(250), nullable=False, unique=True)
    Description = Column('description', String(250), nullable=False, unique=True)
    # Non REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    
class DeskDesk(Base):
    '''
    Desk to Desk connections.
    '''
    __tablename__ = 'workflow_desk_desk'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    source = Column('fk_source_id', ForeignKey(DeskMapped.id), nullable=False, primary_key=True)
    destination = Column('fk_destination_id', ForeignKey(DeskMapped.id), nullable=False, primary_key=True)
    