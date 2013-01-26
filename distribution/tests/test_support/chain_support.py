'''
Created on Nov 24, 2011

@package: tests
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides processing chain support.
'''

from ally.api.config import GET
from ally.container import ioc
from ally.container._impl import ioc_setup
from ally.core.http.spec.server import RequestHTTP, RequestContentHTTP, \
    ResponseContentHTTP, ResponseHTTP
from ally.core.spec.codes import Code
from ally.design.processor import ONLY_AVAILABLE, CREATE_REPORT, Assembly, \
    Processing, Chain
from ally.support.util_io import IInputStream, readGenerator
from urllib.parse import urlparse, parse_qsl
import re

# --------------------------------------------------------------------

def compileProcessings(assembly):
    '''
    Compiles the path assemblies to path processings.
    '''
    assert isinstance(assembly, ioc_setup.Assembly)
    
    ioc.activate(assembly)
    pathAssemblies, pathProcessing = assembly.processForPartialName('pathAssemblies'), []
    ioc.deactivate()
    
    for pattern, assembly in pathAssemblies:
        assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly

        processing, report = assembly.create(ONLY_AVAILABLE, CREATE_REPORT,
                                             request=RequestHTTP, requestCnt=RequestContentHTTP,
                                             response=ResponseHTTP, responseCnt=ResponseContentHTTP)

        print('Assembly report for pattern \'%s\':\n%s' % (pattern, report))
        pathProcessing.append((re.compile(pattern), processing))
        
    return pathProcessing

# --------------------------------------------------------------------

def process(pathProcessing, method, headers, url, source):
    '''
    Process a chain based on the provided path processings.
    '''
    url = urlparse(url)
    path = url.path.lstrip('/')

    for regex, processing in pathProcessing:
        match = regex.match(path)
        if match:
            uriRoot = path[:match.end()]
            if not uriRoot.endswith('/'): uriRoot += '/'

            assert isinstance(processing, Processing), 'Invalid processing %s' % processing
            req, reqCnt = processing.contexts['request'](), processing.contexts['requestCnt']()
            rsp, rspCnt = processing.contexts['response'](), processing.contexts['responseCnt']()
            chain = processing.newChain()

            assert isinstance(chain, Chain), 'Invalid chain %s' % chain
            assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
            assert isinstance(reqCnt, RequestContentHTTP), 'Invalid request content %s' % reqCnt
            assert isinstance(rsp, ResponseHTTP), 'Invalid response %s' % rsp
            assert isinstance(rspCnt, ResponseContentHTTP), 'Invalid response content %s' % rspCnt

            req.scheme, req.uriRoot, req.uri = 'http', uriRoot, path[match.end():]
            req.parameters = parse_qsl(url.query, True, False)
            break
    else: raise Exception('Invalid url')

    req.method = method
    req.headers = headers
    reqCnt.source = source

    chain.process(request=req, requestCnt=reqCnt, response=rsp, responseCnt=rspCnt).doAll()
    
    return req, reqCnt, rsp, rspCnt

def processGet(pathProcessing, headers, url):
    '''
    @see: process
    Process the GET and reads the response stream.
    '''
    _req, _reqCnt, rsp, rspCnt = process(pathProcessing, GET, headers, url, None)
    
    assert isinstance(rsp, ResponseHTTP), 'Invalid response %s' % rsp
    assert isinstance(rspCnt, ResponseContentHTTP), 'Invalid response content %s' % rspCnt
    assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code
    if not rsp.code.isSuccess: raise Exception('Bad response \'%s\' %s' % (rsp.code.code, rsp.text))

    if rspCnt.source is not None:
        if isinstance(rspCnt.source, IInputStream): source = readGenerator(rspCnt.source)
        else: source = rspCnt.source

        for bytes in source: pass  # Just the consume the stream

