'''
Created on Nov 22, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Parses HTML content and generates pre-formatting indexes.
'''

import logging
from ally.design.processor.handler import HandlerProcessor
from content.resource.core.parse.impl.parser import Parser
from ally.design.processor.execution import Chain

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

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
        # TODO: implement

        print('in parser')
