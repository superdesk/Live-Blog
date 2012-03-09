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
from ally.api.type import Iter, Count, List
from introspection.api.plugin import Plugin
from introspection.api.component import Component

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

    @call(countMethod=getMessagesCount)
    def getMessages(self, sourceId:Source.Id=None, offset:int=None, limit:int=10, q:QMessage=None) -> Iter(Message):
        '''
        Provides the messages searched based on the given parameters.
        '''

    def getMessagesCount(self, sourceId:Source.Id=None, q:QMessage=None) -> Count:
        '''
        Provides the total count of messages searched based on the given parameters.
        '''

    @call(countMethod=getComponentMessagesCount)
    def getComponentMessages(self, component:Component.Id, offset:int=None, limit:int=10, q:QMessage=None) -> Iter(Message):
        '''
        Provides the messages for the given component.
        '''

    def getComponentMessagesCount(self, component:Component.Id, q:QMessage=None) -> Count:
        '''
        Provides the total count of messages for the given component.
        '''

    @call(countMethod=getPluginMessagesCount)
    def getPluginMessages(self, plugin:Plugin.Id, offset:int=None, limit:int=10, q:QMessage=None) -> Iter(Message):
        '''
        Provides the messages for the given plugin.
        '''

    def getPluginMessagesCount(self, plugin:Plugin.Id, q:QMessage=None) -> Count:
        '''
        Provides the total count of messages for the given plugin.
        '''
