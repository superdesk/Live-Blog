'''
Created on May 29, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for task-file links API.
'''

from sqlalchemy.schema import Column, ForeignKey
from superdesk.desk.meta.task import TaskMapped
from support.meta.file_link import FileLinkDescription
from superdesk.meta.metadata_superdesk import Base

class FileLinkDB(Base, FileLinkDescription):
    '''
    Provides the mapping for FileLink.
    '''
    __tablename__ = 'desk_task_file'
    
    parent = Column('fk_task_id', ForeignKey(TaskMapped.Id, ondelete='CASCADE'), primary_key=True)

