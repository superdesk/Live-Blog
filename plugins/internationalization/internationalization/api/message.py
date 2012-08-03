'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for localized messages.
'''

from .source import Source
from admin.api.domain_admin import modelAdmin
from admin.introspection.api.component import Component
from admin.introspection.api.plugin import Plugin
from ally.api.config import service, call, query, LIMIT_DEFAULT
from ally.api.criteria import AsLike
from ally.api.type import Iter, List
from ally.support.api.entity import Entity, QEntity, IEntityGetCRUDService
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

@query(Message)
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
    def getMessages(self, sourceId:Source.Id=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
                    qm:QMessage=None, qs:QSource=None) -> Iter(Message):
        '''
        Provides the messages searched based on the given parameters.

        @param sourceId: Source.Id
            The source file identifier.
        @param offset: integer
            Return elements starting from the 'offset' element in the list.
        @param limit: integer
            Return at most 'limit' elements.
        @param detailed: boolean
            If true the returned object will be an extended iterator that will contain details about the iterator part.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''

    @call
    def getComponentMessages(self, component:Component.Id, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
                             qm:QMessage=None, qs:QSource=None) -> Iter(Message):
        '''
        Provides the messages for the given component.

        @param component: Component.Id
            The component identifier.
        @param offset: integer
            Return elements starting from the 'offset' element in the list.
        @param limit: integer
            Return at most 'limit' elements.
        @param detailed: boolean
            If true the returned object will be an extended iterator that will contain details about the iterator part.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''

    @call
    def getPluginMessages(self, plugin:Plugin.Id, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
                          qm:QMessage=None, qs:QSource=None) -> Iter(Message):
        '''
        Provides the messages for the given plugin.

        @param plugin: Plugin.Id
            The plugin identifier.
        @param offset: integer
            Return elements starting from the 'offset' element in the list.
        @param limit: integer
            Return at most 'limit' elements.
        @param detailed: boolean
            If true the returned object will be an extended iterator that will contain details about the iterator part.
        @param qm: QMessage
            Query for filtering the messages based on message attributes. @see QMessage
        @param qs: QSource
            Query for filtering the messages based on the message source. @see QSource
        '''
