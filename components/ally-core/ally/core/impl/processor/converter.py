'''
Created on Aug 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the converters for the response content and request content.
'''

from ally.core.spec.resources import Converter
from ally.core.spec.server import IProcessor, ProcessorsChain, Request, Response
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class ConverterHandler(IProcessor):
    '''
    Provides the standard converters.
     
    Provides on request: [content.contentConverter]
    Provides on response: contentLanguage, contentConverter
    
    Requires on request: content.contentLanguage, accLanguages
    Requires on response: [contentLanguage]
    '''

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp

        rsp.contentConverter = Converter()
        if req.content.contentLanguage:
            req.content.contentConverter = Converter()

        chain.proceed()
