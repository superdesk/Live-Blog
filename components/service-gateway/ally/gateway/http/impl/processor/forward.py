'''
Created on Feb 8, 2013

@package: gateway service
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the forwarding processor.
'''

from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing, Chain
from ally.design.processor.handler import HandlerBranching
from ally.design.processor.processor import Included
from ally.gateway.http.spec.gateway import IRepository, Match, Gateway
from urllib.parse import urlparse, parse_qsl
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    Context for request. 
    '''
    # ---------------------------------------------------------------- Required
    uri = requires(str)
    headers = requires(dict)
    parameters = requires(list)
    match = requires(Match)

# --------------------------------------------------------------------

@injected
class GatewayForwardHandler(HandlerBranching):
    '''
    Implementation for a handler that provides the gateway forward.
    '''
    
    assembly = Assembly
    # The assembly to be used in processing the request for the filters.
    
    def __init__(self):
        assert isinstance(self.assembly, Assembly), 'Invalid assembly %s' % self.assembly
        super().__init__(Included(self.assembly))

    def process(self, chain, processing, request:Request, **keyargs):
        '''
        @see: HandlerBranching.process
        
        Process the forward.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(request, Request), 'Invalid request %s' % request
        if not request.match:
            # No forwarding if there is no match on response
            chain.proceed()
            return  
        
        assert isinstance(request.repository, IRepository), 'Invalid request repository %s' % request.repository
        match = request.match
        assert isinstance(match, Match), 'Invalid response match %s' % match
        assert isinstance(match.gateway, Gateway), 'Invalid gateway %s' % match.gateway
        
        if match.gateway.navigate:
            uri = match.gateway.navigate.replace('*', request.uri)
            try: uri = uri.format(None, *match.groupsURI)
            except IndexError:
                raise Exception('Invalid navigate URI \'%s\' for groups %s' % (match.gateway.navigate, match.groupsURI))
            url = urlparse(uri)
            request.uri = url.path.lstrip('/')
            parameters = parse_qsl(url.query, True, False)
            if request.parameters: parameters.extend(request.parameters)
            request.parameters = parameters
        
        if match.gateway.putHeaders: request.headers.update(match.gateway.putHeaders)
        
        assert log.debug('Forwarding request to \'%s\'', request.uri) or True
        # TODO: Gabriel, this is a temporary fix, we need to provide a handler that properly handles the response and response content
        # isolation.
        nresponse = chain.arg.response.__class__()
        nresponseCnt = chain.arg.responseCnt.__class__()
        chain.update(response=nresponse, responseCnt=nresponseCnt)
        chain.branch(processing)
