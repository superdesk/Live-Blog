'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the file API.
'''

from ..api.file import IFileService, QFile
from ..meta.file import File
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.container.ioc import injected
from ally.container.support import setup

# --------------------------------------------------------------------

@injected
@setup(IFileService)
class FileServiceAlchemy(EntityServiceAlchemy, IFileService):
    '''
    Alchemy implementation for @see: IFileService
    '''

    def __init__(self):
        EntityServiceAlchemy.__init__(self, File, QFile)
