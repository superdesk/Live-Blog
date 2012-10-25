'''
Created on Aug 24, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text base parser processor handler.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import Code, BAD_CONTENT
from ally.support.util_io import IInputStream
from ally.design.context import Context, requires, defines
from ally.design.processor import HandlerProcessor, Chain
from collections import Callable, deque
import abc
import logging
from ally.exception import InputError, Ref
from ally.core.spec.transform.render import Value, List, Object

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoder = requires(Callable)
    decoderData = requires(dict)

class RequestContent(Context):
    '''
    The request content context.
    '''
    # ---------------------------------------------------------------- Required
    type = requires(str)
    charSet = requires(str)
    source = requires(IInputStream)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    errorMessage = defines(str)
    errorDetails = defines(Object)

# --------------------------------------------------------------------

@injected
class ParseBaseHandler(HandlerProcessor):
    '''
    Provides the text base renderer.
    '''

    contentTypes = set
    # The set(string) containing as the content types specific for this parser. 

    def __init__(self):
        assert isinstance(self.contentTypes, set), 'Invalid content types %s' % self.contentTypes
        super().__init__()

    def process(self, chain, request:Request, requestCnt:RequestContent, response:Response, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Parse the request object.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert callable(request.decoder), 'Invalid request decoder %s' % request.decoder
        assert isinstance(request.decoderData, dict), 'Invalid request decoder data %s' % request.decoderData
        assert isinstance(requestCnt.source, IInputStream), 'Invalid request content stream %s' % requestCnt.source
        assert isinstance(requestCnt.charSet, str), 'Invalid request content character set %s' % requestCnt.charSet

        # Check if the response is for this encoder
        if requestCnt.type in self.contentTypes:
            try:
                error = self.parse(request.decoder, request.decoderData, requestCnt.source, requestCnt.charSet)
                if error: response.code, response.text, response.errorMessage = BAD_CONTENT, 'Illegal content', error
            except InputError as e:
                response.code, response.text = BAD_CONTENT, 'Bad content'
                response.errorDetails = self.processInputError(e)
            return  # We need to stop the chain if we have been able to provide the parsing
        else:
            assert log.debug('The content type \'%s\' is not for this %s parser', requestCnt.type, self) or True

        chain.proceed()

    def processInputError(self, e):
        '''
        Process the input error into an error object.
        
        @return: Object
            The object containing the details of the input error.
        '''
        assert isinstance(e, InputError), 'Invalid input error %s' % e

        messages, names, models, properties = deque(), deque(), {}, {}
        for msg in e.message:
            assert isinstance(msg, Ref)
            if not msg.model:
                messages.append(Value('message', msg.message))
            elif not msg.property:
                messagesModel = models.get(msg.model)
                if not messagesModel: messagesModel = models[msg.model] = deque()
                messagesModel.append(Value('message', msg.message))
                if msg.model not in names: names.append(msg.model)
            else:
                propertiesModel = properties.get(msg.model)
                if not propertiesModel: propertiesModel = properties[msg.model] = deque()
                propertiesModel.append(Value(msg.property, msg.message))
                if msg.model not in names: names.append(msg.model)

        errors = deque()
        if messages: errors.append(List('error', *messages))
        for name in names:
            messagesModel, propertiesModel = models.get(name), properties.get(name)

            props = deque()
            if messagesModel: props.append(List('error', *messagesModel))
            if propertiesModel: props.extend(propertiesModel)

            errors.append(Object(name, *props))

        return Object('model', *errors)

    # ----------------------------------------------------------------

    @abc.abstractclassmethod
    def parse(self, decoder, data, source, charSet):
        '''
        Parse the input stream using the decoder.
        
        @param decoder: callable
            The decoder to be used by the parsing.
        @param data: dictionary{string, object}
            The data used for the decoder.
        @param source: IInputStream
            The byte input stream containing the content to be parsed.
        @param charSet: string
            The character set for the input source stream.
        @return: string|None
            If a problem occurred while parsing and decoding it will return a detailed error message, if the parsing is
            successful a None value will be returned.
        '''

