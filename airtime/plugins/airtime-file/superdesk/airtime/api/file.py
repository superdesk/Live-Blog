'''
Created on Oct 1, 2012

@package: airtime file
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for airtime files.
'''

from ally.api.config import service, call
from ally.api.type import Iter
from ally.support.api.entity import Entity
from superdesk.airtime.api.domain_airtime import modelAirtime


# --------------------------------------------------------------------

@modelAirtime
class File(Entity):
    '''
    This contains the audio file data.
    '''
    Name = str

# --------------------------------------------------------------------

@service
class IFileService:
    '''
    Provides the File entities.
    '''
    
    @call
    def getAll(self) -> Iter(File):
        '''
        Provides all the available files.
        '''
    
