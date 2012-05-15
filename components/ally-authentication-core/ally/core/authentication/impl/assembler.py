'''
Created on Jun 18, 2011

@package: ally authenticated core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the call assemblers used for authentication.
'''

from ally.api.operator.authentication.type import IAuthenticated, \
    TypeAuthentication, TypeModelAuth
from ally.api.operator.type import TypeModel, TypeModelProperty
from ally.api.type import Input, typeFor
from ally.container.ioc import injected
from ally.core.spec.resources import Node, Invoker, IAssembler, AssembleError
import logging
from ally.core.impl.invoker import InvokerRestructuring

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class AssembleAuthenticated(IAssembler):
    '''
    This assembler will wrap any invoker that has an authenticated property in order to have them mapped without the
    possibility of providing the authenticated data, which will populated by the wrapping invokers. This should always
    be the first assemblers in order to ensure that the other assemblers will work with the wrapped invokers.
    '''

    def knownModelHints(self):
        '''
        @see: IAssembler.knownModelHints
        '''
        return {}

    def knownCallHints(self):
        '''
        @see: IAssembler.knownCallHints
        '''
        return {}

    def assemble(self, root, invokers):
        '''
        @see: IAssembler.assemble
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invokers, list), 'Invalid invokers %s' % invokers
        invokersAuth = []
        while invokers:
            invoker = self.process(invokers.pop())
            if invoker is not None: invokersAuth.append(invoker)
        invokers.extend(invokersAuth)

    # ----------------------------------------------------------------

    def process(self, invoker):
        '''
        Processes the invoker to an authenticated invoker.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert not isinstance(invoker.output, IAuthenticated), 'Invalid authenticated output for %s' % invoker

        index, inputs, indexes, indexesSetValue, authTypes = 0, [], [], {}, set()
        for k, inp in enumerate(invoker.inputs):
            assert isinstance(inp, Input), 'Invalid input %s' % inp
            typ = inp.type
            if isinstance(typ, IAuthenticated):
                indexes.append(typ)
                authTypes.add(typ)
            else:
                inputs.append(inp)
                indexes.append(index)
                index += 1

            if isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                for prop, ptyp in typ.container.properties.items():
                    if isinstance(ptyp, TypeModelAuth):
                        assert isinstance(ptyp, TypeModelAuth)
                        ptyp = typeFor(getattr(ptyp.forClass, ptyp.container.propertyId))
                        # We need to get the property of the authenticated model.
                        assert isinstance(ptyp, IAuthenticated), 'Invalid authenticated type %s' % ptyp
                        authTypes.add(ptyp)
                        toSet = indexesSetValue.get(k)
                        if not toSet: indexesSetValue[k] = {prop:ptyp}
                        else: toSet[prop] = ptyp

        if authTypes:
            authIndexes = {}
            for typ in authTypes:
                name = ['auth$']
                if isinstance(typ, TypeModel):
                    name.append(typ.container.name)
                elif isinstance(typ, TypeModelProperty):
                    name.append(typ.container.name)
                    name.append('.')
                    name.append(typ.property)
                else:
                    raise AssembleError('Unknown authenticated type %s' % typ)
                authIndexes[typ] = len(inputs)
                inputs.append(Input(''.join(name), TypeAuthentication(typ), True, None))

            # Now we replace the indexes where the authenticated types where
            for k in range(0, len(indexes)):
                typ = indexes[k]
                if isinstance(typ, IAuthenticated): indexes[k] = authIndexes[typ]

            for toSet in indexesSetValue.values():
                for prop in list(toSet):
                    typ = toSet[prop]
                    if isinstance(typ, IAuthenticated): toSet[prop] = authIndexes[typ]

            invoker = InvokerRestructuring(invoker, inputs, indexes, indexesSetValue)
            log.info('Assembled as an authenticated invoker %s' % invoker)
            return invoker
