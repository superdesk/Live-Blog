'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for text item.
'''

import json
from codecs import getwriter
from io import BytesIO
from ally.api.validate import validate
from ally.container.support import setup
from content.resource.api.item_text import IItemTextService, ItemText,\
    CONTENT_TYPE_TEXT
from content.resource.meta.mengine.item_text import ItemTextMapped
from mongo_engine.impl.entity import EntityServiceMongo, EntitySupportMongo
from ally.cdm.spec import ICDM, PathNotFound
from ally.container import wire
from ally.design.processor.assembly import Assembly
from ally.design.processor.context import Context
from ally.design.processor.attribute import defines, requires
from ally.support.util_io import IInputStream, pipe
from content.resource.api.item_resource import TYPE_RESOURCE, QItemResource
from content.base.api.item import Item
from ally.design.processor.execution import FILL_ALL
from mongo_engine.support.util_service import insertModel, updateModel
from ally.api.model import Content

# --------------------------------------------------------------------

class Parser(Context):
    '''
    Context used by the content parser processors. 
    '''
    # ---------------------------------------------------------------- Defined
    content = defines(IInputStream, doc='''
    The content to be parsed.
    ''')
    charSet = defines(str, doc='''
    The content character set
    ''')
    type = defines(str, doc='''
    The content mime type
    ''')
    # ---------------------------------------------------------------- Required
    textPlain = requires(IInputStream, doc='''
    The text content with the formatting removed
    ''')
    formatting = requires(dict, doc='''
    @rtype: dict
    Dictionary of index:formatting tag pairs identifying formatting tags in the
    plain text content.
    ''')

# --------------------------------------------------------------------

PLAIN_TEXT_EXT = 'txt'
JSON_EXT = 'json'

@setup(IItemTextService, name='itemTextService')
@validate(ItemTextMapped)
class ItemTextServiceMongo(EntityServiceMongo, IItemTextService):
    '''
    Implementation for @see: IItemTextService
    '''
    cdmItem = ICDM; wire.entity('cdmItem')
    # the content delivery manager where to publish item content
    
    assemblyParseContent = Assembly; wire.entity('assemblyParseContent')
    # assembly from which to generate processing for text items
    
    def __init__(self):
        '''
        Construct the text content item service
        '''
        EntitySupportMongo.__init__(self, ItemTextMapped, QItemResource)

    def asHTML(self, guid):
        '''
        Implementation for @see IItemTextService.asHTML
        '''
        # TODO: implement
        return None

    def insert(self, item, content):
        '''
        Implementation for @see IItemTextService.insert
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        assert isinstance(content, Content), 'Invalid content %' % content
                
        item.Type = TYPE_RESOURCE
        item.ContentType = CONTENT_TYPE_TEXT

        item.MimeType = content.type

        cntStream = BytesIO()
        pipe(content, cntStream)
        cntStream.seek(0)

        processing = self.assemblyParseContent.create(parser=Parser)
        parser = processing.ctx.parser(content=cntStream, charSet=content.charSet, type=content.type)
        args = processing.execute(FILL_ALL, parser=parser)
        
        cntStream.seek(0)
        
        self.cdmItem.publishContent(item.GUID, cntStream, {})
        self.cdmItem.publishContent('%s.%s' % (item.GUID, PLAIN_TEXT_EXT), args.parser.textPlain, {})
        
        # publish formatting file in CDM
        fStream = BytesIO()
        writer = getwriter(content.charSet if content.charSet else 'utf-8')(fStream)
        json.dump(args.parser.formatting, writer)
        fStream.seek(0)
        self.cdmItem.publishContent('%s.%s' % (item.GUID, JSON_EXT), writer, {})

        item.ContentSet = self.cdmItem.getURI(item.GUID)
        
        return insertModel(ItemTextMapped, item).GUID

    def update(self, item, content=None):
        '''
        Implementation for @see IItemTextService.update
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        if content is not None:
            assert isinstance(content, Content), 'Invalid content %' % content
            self.cdmItem.publishContent(item.GUID, content)
            item.ContentSet = self.cdmItem.getURI(item.GUID)
        if item.Type == TYPE_RESOURCE and ItemText.ContentType in item and item.Class == CONTENT_TYPE_TEXT:
            updateModel(ItemTextMapped, item)
            return True
        return False

    def delete(self, guid):
        '''
        Implementation for @see IItemTextService.delete
        '''
        assert isinstance(guid, str), 'Invalid item %s' % guid
        super().delete(guid)
        try:
            self.cdmItem.remove(guid)
            self.cdmItem.remove('%s.%s' % (guid, PLAIN_TEXT_EXT))
            self.cdmItem.remove('%s.%s' % (guid, JSON_EXT))
        except PathNotFound: pass
        return True
