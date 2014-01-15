'''
Created on Nov 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for text item handler.
'''

import json
from io import BytesIO
from content.base.core.spec import IItemHandler
from sql_alchemy.support.util_service import SessionSupport, insertModel,\
    updateModel
from ally.container.support import setup
from content.resource.api.item_text import ItemText, CLASS_TEXT
from content.base.api.item import Item
from content.resource.core.impl.item_resource import TYPE_RESOURCE
from content.resource.meta.item_text import ItemTextMapped
from ally.cdm.spec import ICDM, PathNotFound
from ally.container import wire
from ally.api.model import Content
from ally.design.processor.assembly import Assembly
from ally.design.processor.execution import FILL_ALL
from ally.design.processor.context import Context
from ally.design.processor.attribute import defines, requires
from ally.support.util_io import IInputStream, pipe
from codecs import getwriter

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

@setup(IItemHandler, name='itemTextHandler')
class ItemTextHandlerAlchemy(SessionSupport, IItemHandler):
    '''
    Handler for text item processing.
    '''
    cdmItem = ICDM; wire.entity('cdmItem')
    # the content delivery manager where to publish item content
    
    assemblyParseContent = Assembly; wire.entity('assemblyParseContent')
    # assembly from which to generate processing for text items

    def register(self, models):
        '''
        Implementation for @see IItemHandler.register
        '''
        assert isinstance(models, set), 'Invalid models set %s' % models
        models.add(ItemText)
    
    def insert(self, item, content=None):
        '''
        Implementation for @see IItemHandler.insert
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        if item.Type == TYPE_RESOURCE and ItemText.Class in item and item.Class == CLASS_TEXT:
            assert isinstance(content, Content), 'Invalid content %' % content
            
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
        Implementation for @see IItemHandler.update
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        if content is not None:
            assert isinstance(content, Content), 'Invalid content %' % content
            self.cdmItem.publishContent(item.GUID, content)
            item.ContentSet = self.cdmItem.getURI(item.GUID)
        if item.Type == TYPE_RESOURCE and ItemText.Class in item and item.Class == CLASS_TEXT:
            updateModel(ItemTextMapped, item)
            return True
        return False

    def delete(self, item):
        '''
        Implementation for @see IItemHandler.delete
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        try:
            self.cdmItem.remove(item.GUID)
            self.cdmItem.remove('%s.%s' % (item.GUID, PLAIN_TEXT_EXT))
            self.cdmItem.remove('%s.%s' % (item.GUID, JSON_EXT))
        except PathNotFound: pass
        return True
