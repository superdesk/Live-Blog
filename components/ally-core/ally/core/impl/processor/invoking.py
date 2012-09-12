'''
Created on Jun 30, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invoking handler.
'''

from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.api.operator.type import TypeModelProperty
from ally.api.type import Input
from ally.core.spec.codes import DELETED_SUCCESS, CANNOT_DELETE, UPDATE_SUCCESS, \
    CANNOT_UPDATE, INSERT_SUCCESS, CANNOT_INSERT, BAD_CONTENT, Code, \
    METHOD_NOT_AVAILABLE, INCOMPLETE_ARGUMENTS, INPUT_ERROR
from ally.core.spec.resources import Path, Invoker
from ally.core.spec.transform.render import Object, List, Value
from ally.design.context import Context, defines, requires
from ally.design.processor import HandlerProcessorProceed
from ally.exception import DevelError, InputError, Ref
from collections import deque
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    method = requires(int)
    path = requires(Path)
    invoker = requires(Invoker)
    arguments = requires(dict)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    errorMessage = defines(str)
    errorDetails = defines(Object)
    obj = defines(object, doc='''
    @rtype: object
    The response object.
    ''')

# --------------------------------------------------------------------

class InvokingHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that makes the actual call to the request method corresponding invoke on the
    resource path node. The invoking will use all the obtained arguments from the previous processors and perform
    specific actions based on the requested method. In GET case it will provide to the request the invoke returned
    object as to be rendered to the response, in DELETE case it will stop the execution chain and send as a response
    a success code.
    '''

    def __init__(self):
        '''
        Construct the handler.
        '''
        super().__init__()

        self.invokeCallBack = {
                               GET: self.afterGet,
                               INSERT: self.afterInsert,
                               UPDATE: self.afterUpdate,
                               DELETE: self.afterDelete
                               }

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Invoke the request invoker.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error

        assert isinstance(request.path, Path), 'Invalid request path %s' % request.path
        assert isinstance(request.invoker, Invoker), 'Invalid invoker %s' % request.invoker

        callBack = self.invokeCallBack.get(request.method)
        if callBack is None:
            response.code, response.text = METHOD_NOT_AVAILABLE, 'Cannot process method'
            response.errorMessage = 'Method cannot be processed for invoker \'%s\', something is wrong in the setups'
            response.errorMessage %= request.invoker.name
            return

        arguments = deque()
        for inp in request.invoker.inputs:
            assert isinstance(inp, Input), 'Invalid input %s' % inp
            if inp.name in request.arguments: arguments.append(request.arguments[inp.name])
            elif inp.hasDefault: arguments.append(inp.default)
            else:
                response.code, response.text = INCOMPLETE_ARGUMENTS, 'Missing argument value'
                response.errorMessage = 'No value for mandatory input \'%s\' for invoker \'%s\''
                response.errorMessage %= (inp.name, request.invoker.name)
                log.info('No value for mandatory input %s for invoker %s', inp, request.invoker)
                return
        try:
            value = request.invoker.invoke(*arguments)
            assert log.debug('Successful on calling invoker \'%s\' with values %s', request.invoker,
                             tuple(arguments)) or True

            callBack(request.invoker, value, response)
        except DevelError as e:
            assert isinstance(e, DevelError)
            response.code, response.text = BAD_CONTENT, 'Invoking problem'
            response.errorMessage = e.message
            log.warn('Problems with the invoked content: %s', e.message, exc_info=True)
        except InputError as e:
            assert isinstance(e, InputError)
            response.code, response.text = INPUT_ERROR, 'Input error'
            response.errorDetails = self.processInputError(e)
            assert log.debug('User input exception: %s', e, exc_info=True) or True

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

    def afterGet(self, invoker, value, response):
        '''
        Process the after get action on the value.
        
        @param invoker: Invoker
            The invoker used.
        @param value: object
            The value returned.
        @param response: Response
            The response to set the error if is the case.
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response

        response.obj = value

    def afterInsert(self, invoker, value, response):
        '''
        Process the after insert action on the value.
        
        @param invoker: Invoker
            The invoker used.
        @param value: object
            The value returned.
        @param response: Response
            The response to set the error if is the case.
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(response, Response), 'Invalid response %s' % response

        if isinstance(invoker.output, TypeModelProperty) and \
        invoker.output.container.propertyId == invoker.output.property:
            if value is not None:
                response.obj = value
            else:
                response.code, response.text = CANNOT_INSERT, 'Cannot insert'
                assert log.debug('Cannot insert resource') or True
                return
        else:
            response.obj = value
        response.code, response.text = INSERT_SUCCESS, 'Successfully created'

    def afterUpdate(self, invoker, value, response):
        '''
        Process the after update action on the value.
        
        @param invoker: Invoker
            The invoker used.
        @param value: object
            The value returned.
        @param response: Response
            The response to set the error if is the case.
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(response, Response), 'Invalid response %s' % response

        if invoker.output.isOf(None):
            response.code, response.text = UPDATE_SUCCESS, 'Successfully updated'
            assert log.debug('Successful updated resource') or True
        elif invoker.output.isOf(bool):
            if value == True:
                response.code, response.text = UPDATE_SUCCESS, 'Successfully updated'
                assert log.debug('Successful updated resource') or True
            else:
                response.code, response.text = CANNOT_UPDATE, 'Cannot update'
                assert log.debug('Cannot update resource') or True
        else:
            #If an entity is returned than we will render that.
            response.code, response.text = UPDATE_SUCCESS, 'Successfully updated'
            response.obj = value

    def afterDelete(self, invoker, value, response):
        '''
        Process the after delete action on the value.
        
        @param invoker: Invoker
            The invoker used.
        @param value: object
            The value returned.
        @param response: Response
            The response to set the error if is the case.
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(response, Response), 'Invalid response %s' % response

        if invoker.output.isOf(bool):
            if value == True:
                response.code, response.text = DELETED_SUCCESS, 'Successfully deleted'
                assert log.debug('Successfully deleted resource') or True
            else:
                response.code, response.text = CANNOT_DELETE, 'Cannot delete'
                assert log.debug('Cannot deleted resource') or True
        else:
            #If an entity is returned than we will render that.
            response.code, response.text = DELETED_SUCCESS, 'Successfully deleted'
            response.obj = value
