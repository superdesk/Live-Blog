'''
Created on Jun 28, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the implementation for the resources manager.
'''

from ally.api.operator.container import Service, Call
from ally.api.operator.type import TypeService, TypeModel, TypeModelProperty
from ally.api.type import Input, typeFor
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerCall
from ally.core.spec.resources import Node, IAssembler, IResourcesRegister, \
    InvokerInfo, Invoker
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ResourcesRegister(IResourcesRegister):
    '''
    @see: IResourcesRegister, IResourcesLocator implementations.
    '''

    root = Node
    # The root node for the resource manager.
    assemblers = list
    # The list of assemblers to be used by this resources manager in order to register nodes.

    def __init__(self):
        assert isinstance(self.root, Node), 'Invalid root node %s' % self.root
        assert isinstance(self.assemblers, list), 'Invalid assemblers list %s' % self.assemblers

        self._hintsCall, self._hintsModel = {}, {}
        for asm in self.assemblers:
            assert isinstance(asm, IAssembler), 'Invalid assembler %s' % asm
            known = asm.knownCallHints()
            if known: self._hintsCall.update(known)
            known = asm.knownModelHints()
            if known: self._hintsModel.update(known)

    def register(self, implementation):
        '''
        @see: IResourcesRegister.register
        '''
        assert implementation is not None, 'A implementation is required'
        typeService = typeFor(implementation)
        assert isinstance(typeService, TypeService), 'Invalid service implementation %s' % implementation
        service = typeService.service
        assert isinstance(service, Service), 'Invalid service %s' % service

        log.info('Assembling node structure for service %s', service)
        invokers = []
        for call in service.calls.values():
            assert isinstance(call, Call), 'Invalid call %s' % call
            if __debug__:
                unknown = set(call.hints.keys()).difference(self._hintsCall.keys())

                fnc = getattr(typeService.clazz, call.name).__code__
                try: name = fnc.__name__
                except AttributeError: name = call.name
                location = (fnc.co_filename, fnc.co_firstlineno, name)

                assert not unknown, \
                'Allowed call hints are:\n\t%s\nInvalid call hints %r at:\nFile "%s", line %i, in %s' % \
                (('\n\t'.join('"%s": %s' % item for item in self._hintsCall.items()), ', '.join(unknown)) + location)

                for inp in call.inputs:
                    assert isinstance(inp, Input), 'Invalid input %s' % inp
                    if isinstance(inp.type, (TypeModel, TypeModelProperty)):
                        unknown = set(inp.type.container.hints.keys()).difference(self._hintsModel.keys())

                        assert not unknown, \
                        'Allowed model hints are:\n\t%s\nInvalid model hints %r at for %s:\nFile "%s", line %i, in %s' % \
                        (('\n\t'.join('"%s": %s' % item for item in self._hintsModel.items()), ', '.join(unknown),
                          inp.type) + location)

            invokers.append(InvokerCall(implementation, call))

        for asm in self.assemblers:
            assert isinstance(asm, IAssembler)
            asm.assemble(self.root, invokers)
        for invoker in invokers:
            assert isinstance(invoker, Invoker)
            info = invoker.infoAPI or invoker.infoIMPL
            assert isinstance(info, InvokerInfo)
            log.warning('Could not resolve in the node structure the call at:\nFile "%s", line %i, in %s', \
                        info.file, info.line, info.name)
