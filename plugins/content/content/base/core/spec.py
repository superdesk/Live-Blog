'''
Created on Nov 12, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Specifications for item handlers.
'''

import abc

# --------------------------------------------------------------------

class IItemHandler(metaclass=abc.ABCMeta):
    '''
    Handler for specialized item processing.
    '''
    
    @abc.abstractmethod
    def register(self, models):
        '''
        Register models processed by this handler.
        
        @param models: set
            Set of the existing models
        '''
    
    @abc.abstractmethod
    def insert(self, item, content=None):
        '''
        Insert an item and it's corresponding binary content (if the item had a content)
        
        @param item: Item
            The item object to be inserted
        @param content: Content
            The item corresponding binary content
        @return: Item.GUID|None
            Return the item GUID if this handler can process the request, None otherwise
        '''

    @abc.abstractmethod
    def update(self, item, content=None):
        '''
        Update the item and it's corresponding binary content (if the item had a content)
        
        @param item: Item
            The item object to be updated
        @param content: Content
            The item corresponding binary content
        @return: bool
            Return True if this handler can process the request, False otherwise
        '''

    @abc.abstractmethod
    def delete(self, item):
        '''
        Delete the item and it's corresponding binary content (if the item had a content)
        
        @param item: Item
            The item object to be deleted
        @return: bool
            Return True if this handler can process the request and the item can be deleted,
            False otherwise
        '''
