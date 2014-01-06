'''
Created on Nov 22, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Parses HTML content and generates pre-formatting indexes.
'''

import logging
from io import BytesIO
from codecs import getwriter
from ally.design.processor.handler import HandlerProcessor
from ally.design.processor.execution import Chain
from ally.design.processor.context import Context
from ally.design.processor.attribute import defines, requires
from ally.support.util_io import IInputStream
from content.resource.core.parse.impl.html_parser import TextItemHMTLParser

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Parser(Context):
    '''
    Context used by the content parser processors. 
    '''
    # ---------------------------------------------------------------- Defined
    textPlain = defines(IInputStream, doc='''
    The text content with the formatting removed
    ''')
    formatting = defines(dict, doc='''
    @rtype: dict
    Dictionary of index:formatting tag pairs identifying formatting tags in the
    plain text content.
    ''')
    # ---------------------------------------------------------------- Required
    content = requires(IInputStream, doc='''
    The content to be parsed.
    ''')
    charSet = requires(str, doc='''
    The content character set
    ''')
    type = requires(str, doc='''
    The content mime type
    ''')

# --------------------------------------------------------------------

class ParserHTMLHandler(HandlerProcessor):
    '''
    Implementation for a processor that parses HTML files and creates an index of
    formatting tags.
    '''

    def __init__(self):
        super().__init__()

    def process(self, chain, parser:Parser, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Parse the given content and generate the pre-formatting index.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(parser, Parser), 'Invalid parser %s' % parser

        if not parser.content: return
        assert isinstance(parser.content, IInputStream), 'Invalid content %s' % parser.content
        if not parser.type or parser.type.lower() != 'text/html': return
        
        outb = BytesIO()
        outw = getwriter(parser.charSet if parser.charSet else 'utf-8')(outb)

        parserHTML = TextItemHMTLParser(strict=False)
        parser.formatting = parserHTML.parse(parser.content, parser.charSet if parser.charSet else 'utf-8', outw)
        
        outb.seek(0)
        
        parser.textPlain = outb
