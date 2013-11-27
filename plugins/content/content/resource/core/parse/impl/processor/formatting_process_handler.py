'''
Created on Nov 25, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Generates plain text and final formatting from pre-formatting indexes and
original content.
'''

import logging
from ally.design.processor.handler import HandlerProcessor
from ally.design.processor.context import Context
from ally.design.processor.attribute import defines, requires
from ally.api.model import Content
from ally.design.processor.execution import Chain

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Parser(Context):
    '''
    Context used by the content parser processors. 
    '''
    # ---------------------------------------------------------------- Defined
    textPlain = defines(Content, doc='''
    The content in plain text format.
    ''')
    formatting = defines(dict, doc='''
    @rtype: dict
    Dictionary of index:formatting tag pairs identifying formatting tags in the
    plain text content.
    ''')
    # ---------------------------------------------------------------- Required
    content = requires(Content, doc='''
    The content to be parsed.
    ''')
    preFormatting = requires(dict, doc='''
    @rtype: dict
    Dictionary of index:formatting tag pairs identifying formatting tags in the
    original content.
    ''')

# --------------------------------------------------------------------

class FormattingProcessorHandler(HandlerProcessor):
    '''
    Implementation for a processor that transforms the original content
    in plain text and the pre-formatting into the final formatting index.
    The pre-formatting index applies to the original content while the
    final formatting index applies to the plain text version.
    '''

    def __init__(self):
        super().__init__()

    def process(self, chain, generator:Parser, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Transform the original content in plain text and the pre-formatting
        index to the final formatting index.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(generator, Parser), 'Invalid formatting generator %s' % generator

        if not generator.content: return
        if not generator.preFormatting: return
        
        # TODO: implement
        
        print('in formatting processor')
