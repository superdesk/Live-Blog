'''
Created on Mar 14, 2013

@package: content publisher
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugur

API implementation for content publisher.
'''

from ally.container.support import setup
from content.publisher.api.publisher import IContentPublisherService
from ally.container.ioc import injected
from ally.container import wire
import mongoengine
from content.publisher.meta.publisher import Item
import datetime

# --------------------------------------------------------------------

@injected
@setup(IContentPublisherService, name='publisherService')
class ContentPublisherService(IContentPublisherService):
    '''
    Implementation for @see: IContentPublisherService
    '''

    mongodb_server = 'localhost'; wire.config('mongodb_server', doc='''The address of the mongoDb server''')
    mongodb_port = 27017; wire.config('mongodb_port', doc='''The port of the mongoDb server''')
    mongodb_database = 'superdesk'; wire.config('mongodb_database', doc='''The name of the mongoDb database''')

    def __init__(self):
        '''
        Construct the content publisher service.
        '''
        
        assert isinstance(self.mongodb_server, str), 'Invalid mongoDb server address %s' % self.mongodb_server
        assert isinstance(self.mongodb_port, int), 'Invalid mongoDb server port %s' % self.mongodb_port
        assert isinstance(self.mongodb_database, str), 'Invalid mongoDb database name %s' % self.mongodb_database
        
        mongoengine.connect(self.mongodb_database, host=self.mongodb_server, port=self.mongodb_port)


    def publish(self, guid):
        '''
        Implementation for @see: IContentPublisherService.publish   
        '''
        #Test add document
        
        item = Item()
        
        item.guid = guid
        item.version = 1
        item.itemClass = Item.CLASS_TEXT
        item.urgency = 'urgency'
        item.headline = 'headline'
        item.slugline = 'slugline'
        item.byline = 'byline'
        item.creditline = 'creditline'
        item.firstCreated = datetime.datetime.now()
        item.versionCreated = datetime.datetime.now()
        
        item.save(safe=True)
        
        print("Added doc with id=", str(item.id))
        
        return True
           
    def unpublish(self, guid): 
        '''
        Implementation for @see: IContentPublisherService.unpublish      
        ''' 
        #Test delete document
        Item.objects(guid=guid).delete(safe=True)
        return True
        