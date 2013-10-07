'''
Created on Mar 8, 2013

@package: content publisher
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugur

API specifications for content publisher.
'''

from ally.api.config import service, call, DELETE, UPDATE
from content.packager.api.item import Item

@service
class IContentPublisherService:
    '''
    Provides the service methods for content publisher model.
    '''

    @call(method=UPDATE, webName='aPublish')
    def publish(self, guid:Item.GUId) -> bool:
        '''
        Publish the item that has the given Guid. Return true if the operation is with success,
        false if the Guid don't exists.    
        '''
        
    @call(method=DELETE, webName='aUnpublish')    
    def unpublish(self, guid:Item.GUId) -> bool: 
        '''
        Unpublish the item that has the given Guid. Return true if the operation is with success,
        false if the Guid don't exists.    
        '''   