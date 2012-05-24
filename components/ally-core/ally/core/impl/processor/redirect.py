'''
Created on Apr 12, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content location redirect based on references.
'''

from ally.api.operator.type import TypeModelProperty
from ally.api.type import TypeReference
from ally.container.ioc import injected
from ally.core.spec.server import IProcessor, ProcessorsChain, Response, Request, \
    EncoderPath, Processors
import logging
from ally.core.spec.codes import REDIRECT

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class RedirectHandler(IProcessor):
    '''
    Implementation for a processor that provides the redirect by using the content location based on found references.
    
    Provides on request: NA
    Provides on response: [contentLocation]
    
    Requires on request: NA
    Requires on response: objType, encoderPath
    '''

    redirects = Processors
    # The redirects processors, at the end of the processors chain there needs to be and obj on the response that will
    # be used as the redirect path.

    def __init__(self):
        assert isinstance(self.redirects, Processors), 'Invalid redirects processors %s' % self.redirects

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        if not rsp.objType:
            assert log.debug('There is no object type on the response, no redirect to process') or True
        elif not rsp.encoderPath:
            assert log.debug('There is no path encoder on the response, cannot perform redirect') or True
        else:
            assert isinstance(rsp.encoderPath, EncoderPath), 'Invalid encoder path %s' % rsp.encoderPath
            typ = rsp.objType
            if isinstance(typ, TypeModelProperty): typ = typ.type
            if isinstance(typ, TypeReference):
                self.redirects.newChain().process(req, rsp)
                if rsp.code and rsp.code.isSuccess:
                    assert isinstance(rsp.obj, str), 'Invalid response object %s from redirects processing' % rsp.obj
                    rsp.location = rsp.encoderPath.encode(rsp.obj)
                    rsp.setCode(REDIRECT, 'Redirect')
                return

        chain.proceed()
