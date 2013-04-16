'''
Created on Aug 8, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the integration of the additional arguments into the main arguments.
'''

from ally.api.type import Input, typeFor
from ally.core.spec.resources import Invoker, Path
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed

# --------------------------------------------------------------------

class RequestProvide(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Defined
    arguments = defines(dict, doc='''
    @rtype: dictionary{string, object}
    The dictionary containing the arguments that will be passes to the invoker that provides the response object.
    ''')
    argumentsOfType = defines(dict, doc='''
    @rtype: dictionary{Type, object}
    A dictionary containing as a key the argument type, this dictionary needs to be populated by the 
    processors with any system values that might be used for invoking, the actual use of this arguments depends
    ''')

# --------------------------------------------------------------------

class ArgumentsPrepareHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the integration of the additional arguments into the invoke arguments.
    This processor will provide the argument by type.
    '''

    def process(self, request:RequestProvide, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provides the additional arguments by type to be populated.
        '''
        assert isinstance(request, RequestProvide), 'Invalid request %s' % request

        request.argumentsOfType = {}
        request.arguments = {}

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    path = requires(Path)
    invoker = requires(Invoker)
    argumentsOfType = requires(dict)
    arguments = requires(dict)

# --------------------------------------------------------------------

class ArgumentsBuildHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the integration of the additional arguments into the invoke arguments.
    '''

    def process(self, request:Request, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Transpose the additional arguments into the main arguments.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        if request.invoker is None: return  # If there is no invoker it means that no arguments need to be processed
        assert isinstance(request.path, Path), 'Invalid request path %s' % request.path
        assert isinstance(request.invoker, Invoker), 'Invalid request invoker %s' % request.invoker

        if request.argumentsOfType:
            for inp in request.invoker.inputs:
                assert isinstance(inp, Input), 'Invalid input %s' % inp

                if inp.name in request.arguments: continue

                for argType, value in request.argumentsOfType.items():
                    if typeFor(argType) == inp.type:
                        if inp.name not in request.arguments: request.arguments[inp.name] = value
                        break

        request.arguments.update(request.path.toArguments(request.invoker))
