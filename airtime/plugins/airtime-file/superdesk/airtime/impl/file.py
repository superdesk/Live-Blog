'''
Created on Oct 1, 2012

@package: airtime file
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Airtime file implementation.
'''

from ally.support.sqlalchemy.session import SessionSupport
from superdesk.airtime.api.file import IFileService
from superdesk.airtime.meta.file import FileMapped
from ally.container.ioc import injected
from ally.container.support import setup

# --------------------------------------------------------------------

@setup(IFileService)
@injected
class FileServiceAlchemy(SessionSupport, IFileService):
    '''
    Implementation using SQLAlchemy for @see: IFileService
    '''
    
    def __init__(self):
        SessionSupport.__init__(self)
        
    def getAll(self):
        '''
        @see: IFileService.getAll
        '''
        sql = self.session().query(FileMapped)
        return sql.all()
