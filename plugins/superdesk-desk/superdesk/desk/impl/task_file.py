'''
Created on May 29, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for the task-file links API.
'''

from ..api.task_file import ITaskFileService
from ..meta.task_file import FileLinkDB
from support.impl.file_link import createFileLinkImpl
from ally.container.ioc import injected
from ally.container.support import setup

# --------------------------------------------------------------------

TaskFileServiceAlchemy = createFileLinkImpl(ITaskFileService, FileLinkDB)
TaskFileServiceAlchemy = setup(ITaskFileService, name='blogConfigurationService')(TaskFileServiceAlchemy)
TaskFileServiceAlchemy = injected()(TaskFileServiceAlchemy)
'''
Implementation for @see: ITaskFileService

This implementation is automatically generated.
See the file_link modules of the support package.
'''
