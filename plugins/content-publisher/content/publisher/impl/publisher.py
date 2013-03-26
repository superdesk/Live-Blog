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
from content.publisher.meta.publisher import Item, Content
from content.packager.api.item import IItemService
from content.packager.api.item_content import IItemContentService, QItemContent, \
    ItemContent
from content.packager.api.item import Item as PackageItem

# --------------------------------------------------------------------

@injected
@setup(IContentPublisherService, name='publisherService')
class ContentPublisherService(IContentPublisherService):
    '''
    Implementation for @see: IContentPublisherService
    '''

    mongodb_server = 'localhost'; wire.config('mongodb_server', doc='''The address of the mongoDb server''')
    mongodb_port = 27017; wire.config('mongodb_port', doc='''The port of the mongoDb server''')
    mongodb_database = 'mongodb'; wire.config('mongodb_database', doc='''The name of the mongoDb database''')

    itemService = IItemService; wire.entity('itemService')
    # item service used to convert article content to NewsML structure
    itemContentService = IItemContentService; wire.entity('itemContentService')
    # item content service used to convert article content to NewsML structure

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
        # Test add document
        myItem = self.itemService.getById(guid)
        assert isinstance(myItem, PackageItem)

        item = Item()
        item.guid = myItem.GUId
        item.version = myItem.Version
        item.itemClass = myItem.ItemClass
        item.urgency = myItem.Urgency
        item.headline = myItem.HeadLine
        item.slugline = myItem.SlugLine
        item.byline = myItem.Byline
        item.creditline = myItem.CreditLine
        item.firstCreated = myItem.FirstCreated
        item.versionCreated = myItem.VersionCreated

        q = QItemContent()
        q.item = myItem.GUId
        contents = self.itemContentService.getAll(q=q)
        for c in contents:
            assert isinstance(c, ItemContent)
            content = Content()
            content.contenttype = c.ContentType
            content.content = c.Content
            content.residRef = c.ResidRef
            content.href = c.HRef
            content.size = c.Size
            content.rendition = c.Rendition
            item.contents.append(content)

        self.unpublish(item.guid)
        item.save(safe=True)
        return True

    def unpublish(self, guid):
        '''
        Implementation for @see: IContentPublisherService.unpublish
        '''
        # Test delete document
        Item.objects(guid=guid).delete(safe=True)
        return True

