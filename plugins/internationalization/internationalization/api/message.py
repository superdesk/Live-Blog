'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for localized messages.
'''

from .source import Source
from ally.api.config import service, call, query
from ally.api.criteria import AsLike
from ally.api.type import Iter, Count, List
from ally.support.api.entity import Entity, QEntity, IEntityGetCRUDService
from introspection.api.domain_admin import modelAdmin
from introspection.api.component import Component
from introspection.api.plugin import Plugin
from internationalization.api.source import QSource

# --------------------------------------------------------------------

@modelAdmin
class Message(Entity):
    '''
    Model for a localized message.
    '''
    Source = Source
    Singular = str
    Plural = List(str)
    Context = str
    LineNumber = int
    Comments = str

# --------------------------------------------------------------------

@query
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

    def getMessagesCount(self, sourceId:Source.Id=None, qm:QMessage=None, qs:QSource=None) -> Count:
        '''
        Provides the total count of messages searched based on the given parameters.
        
        @param sourceId: Source.Id
            The source file identifier.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''

    @call(countMethod=getMessagesCount)
    def getMessages(self, sourceId:Source.Id=None, offset:int=None, limit:int=10,
                    qm:QMessage=None, qs:QSource=None) -> Iter(Message):
        '''
        Provides the messages searched based on the given parameters.

        @param sourceId: Source.Id
            The source file identifier.
        @param offset: int
            Return elements starting from the 'offset' element in the list.
        @param limit: int
            Return at most 'limit' elements.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''

    def getComponentMessagesCount(self, component:Component.Id, qm:QMessage=None, qs:QSource=None) -> Count:
        '''
        Provides the total count of messages for the given component.

        @param component: Component.Id
            The component identifier.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''

    @call(countMethod=getComponentMessagesCount)
    def getComponentMessages(self, component:Component.Id, offset:int=None, limit:int=10,
                             qm:QMessage=None, qs:QSource=None) -> Iter(Message):
        '''
        Provides the messages for the given component.

        @param component: Component.Id
            The component identifier.
        @param offset: int
            Return elements starting from the 'offset' element in the list.
        @param limit: int
            Return at most 'limit' elements.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''

    def getPluginMessagesCount(self, plugin:Plugin.Id, qm:QMessage=None, qs:QSource=None) -> Count:
        '''
        Provides the total count of messages for the given plugin.

        @param plugin: Plugin.Id
            The plugin identifier.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''

    @call(countMethod=getPluginMessagesCount)
    def getPluginMessages(self, plugin:Plugin.Id, offset:int=None, limit:int=10,
                          qm:QMessage=None, qs:QSource=None) -> Iter(Message):
        '''
        Provides the messages for the given plugin.

        @param plugin: Plugin.Id
            The plugin identifier.
        @param offset: int
            Return elements starting from the 'offset' element in the list.
        @param limit: int
            Return at most 'limit' elements.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''

