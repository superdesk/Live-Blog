'''
Created on Jun 13, 2012

@author: chupy
'''

from ally.core.http.impl.processor.header import HeaderHandler
from ally.core.http.impl.processor.headers.content_length import \
    ContentLengthHandler
from ally.core.http.impl.processor.headers.content_type import \
    ContentTypeHandler
from ally.core.http.impl.processor.headers.override_method import \
    MethodOverrideHandler
from ally.core.http.impl.processor.headers.set_fixed import HeaderSetHandler
from ally.core.http.impl.processor.parameter import ParameterHandler
from ally.core.http.impl.processor.uri import URIHandler
from ally.design.processor import assemble
import unittest
from ally.core.http.impl.processor.headers.content_language import ContentLanguageHandler
from ally.core.http.impl.processor.headers.content_disposition import ContentDispositionHandler
from ally.core.http.impl.processor.headers.allow import AllowHandler
from ally.core.http.impl.processor.headers.accept import AcceptHandler
from ally.core.impl.processor.method_invoker import MethodInvokerHandler
from ally.core.babel.processor.text_conversion import BabelConversionHandler
from ally.core.impl.processor.text_conversion import ConversionSetHandler
from ally.core.impl.processor.arguments import ArgumentsHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.sqlalchemy.processor.invoking_transactional import InvokingWithTransactionHandler

# --------------------------------------------------------------------

class TestProcessorAssemble(unittest.TestCase):

    def testAssemble(self):
        handlers = []

        handlersLocators = [URIHandler()]
        handlers.extend(handlersLocators)

        handlersDecode = [HeaderHandler(), MethodOverrideHandler(), ParameterHandler(), ContentTypeHandler(),
                          ContentLengthHandler(), ContentLanguageHandler(), ContentDispositionHandler(),
                          AcceptHandler(), ArgumentsHandler(), MethodInvokerHandler(), BabelConversionHandler(),
                          ConversionSetHandler()]
        handlers.extend(handlersDecode)

        handlersProcess = [InvokingHandler(), InvokingWithTransactionHandler()]
        handlers.extend(handlersProcess)

        handlersEncode = [HeaderSetHandler(), AllowHandler()]
        handlers.extend(handlersEncode)


        assemble(handlers, 'request', 'requestCnt', 'responseCnt', 'response')


# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
