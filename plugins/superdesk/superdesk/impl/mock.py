'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: 

API implementation for article.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.api.mock import IMockService

# --------------------------------------------------------------------

@injected
@setup(IMockService)
class SuperdeskServiceMock(IMockService):
    '''
    '''
    def getById(self):
        return ()
    
