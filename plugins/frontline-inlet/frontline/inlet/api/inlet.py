'''
Created on April 24, 2013

@package: frontline inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for frontline inlet.
'''

from ally.api.config import service, call, GET
from ally.api.type import Iter
from ally.support.api.keyed import Entity
from frontline.api.domain_sms import modelSMS
from superdesk.post.api.post import Post

# --------------------------------------------------------------------

@modelSMS
class Inlet(Entity):
    '''
    Provides the frontline inlet type model.
    '''

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service
class IInletService:
    '''
    Provides the service methods for the frontline inlet.
    '''

    @call(method=GET, webName='Push')
    def pushMessage(self, typeKey:Inlet.Key, phoneNumber:str=None, messageText:str=None, timeStamp:str=None) -> Iter(Post):
        '''
        Inserts a new message.
        TODO: this is a temporary solution, since we do not support the format of FrontlineSMS POST messages
        '''
