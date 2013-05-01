'''
Created on April 24, 2013

@package: frontline inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for frontline sms inlet.
'''

from ally.api.config import service, call, query, GET
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity import Entity, QEntity
from frontline.api.domain_sms import modelSMS
from superdesk.post.api.post import Post
from ..api.inlet import Inlet

# --------------------------------------------------------------------

@modelSMS
class SMS(Entity):
    '''
    Provides the frontline sms model.
    '''

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service((Entity, SMS))
class ISMSService():
    '''
    Provides the service methods for the frontline sms.
    '''

    @call(method=GET, webName='Push')
    def pushMessage(self, typeKey:Inlet.Key, phoneNumber:str, messageText:str) -> Iter(Post):
        '''
        Inserts a new message.
        TODO: this is a temporary solution, since we do not support the format of FrontlineSMS POST messages
        '''

