'''
Created on Aug 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the integration of the additional arguments into the main arguments.
'''

from ally.api.type import Input, typeFor
from ally.core.spec.extension import Invoke, Arguments, ArgumentsAdditional
from ally.core.spec.resources import Invoker
from ally.design.processor import Handler, processor, Chain, mokup

# --------------------------------------------------------------------

@mokup(Invoke, ArgumentsAdditional)
class _Request(Invoke, ArgumentsAdditional, Arguments):
    ''' Used as a mokup class '''

# --------------------------------------------------------------------

class AdditionalArgumentsHandler(Handler):
    '''
    Implementation for a processor that provides the integration of the additional arguments into the invoke arguments.
    '''

    @processor
    def process(self, chain, request:_Request, **keyargs):
        '''
        Populate the additional arguments into the main arguments.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, _Request), 'Invalid request %s' % request
        assert isinstance(request.invoker, Invoker), 'Invalid request invoker %s' % request.invoker

        if request.argumentsOfType:
            for inp in request.invoker.inputs:
                assert isinstance(inp, Input), 'Invalid input %s' % inp

                if inp.name in request.arguments:continue

                for argType, value in request.argumentsOfType.items():
                    if typeFor(argType) == inp.type:
                        request.arguments[inp.name] = value
                        break

        chain.proceed()
