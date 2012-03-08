'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for localized messages.
'''

from .source import Source
from ally.api.config import service, call
from ally.api.criteria import AsLike
from introspection.api import modelDevel
from sql_alchemy.api.entity import Entity, QEntity, IEntityGetCRUDService
from ally.api.type import IterPart, List

# --------------------------------------------------------------------

@modelDevel
class Message(Entity):
    '''
    Model for a localized message.
    '''
    Source = Source.Id
    Singular = str
    Plural = List(str)
    Context = str
    LineNumber = int
    Comments = str
    
# --------------------------------------------------------------------

class QMessage(QEntity):
    '''
    Provides the query for the message.
    '''
    singular = AsLike
    context = AsLike

# --------------------------------------------------------------------

@service((Entity, Message))
class IMessageService(IEntityGetCRUDService):
    '''
    The messages service.
    '''
    
    @call
    def getMessages(self, sourceId:Source.Id=None, offset:int=None, limit:int=10, q:QMessage=None) -> IterPart(Message):
        '''
        Provides the messages searched based on the provided parameters.
        '''
