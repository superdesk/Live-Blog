'''
Created on Jan 8, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC deployment operations.
'''

from ._impl._aop import AOPModules
from ._impl._assembly import Context, Assembly
from ._impl._setup import CallStart
from .error import SetupError
from .impl.priority import sortByPriorities
from inspect import ismodule
import importlib
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def open(*modules, config=None, included=False, active=True):
    '''
    Load and assemble the setup modules and keeps them opened for retrieving and processing values. Call the close
    function after finalization. Automatically activates the assembly.
    
    @param modules: arguments(path|AOPModules|module) 
        The modules that compose the setup.
    @param config: dictionary|None
        The configurations dictionary. This is the top level configurations the values provided here will override any
        other configuration.
    @param included: boolean
        Flag indicating that the newly opened assembly should include the currently active assembly, if this flag is
        True then the opened assembly will have access to the current assembly.
    @param active: boolean
        If true the assembly will be automatically activate, if false then the assembly is only assembled.
    @return: Assembly
        The assembly object.
    '''
    assert isinstance(included, bool), 'Invalid included flag %s' % included
    assert isinstance(active, bool), 'Invalid active flag %s' % active
    context = Context()
    for module in modules:
        if isinstance(module, str): module = importlib.import_module(module)

        if ismodule(module): context.addSetupModule(module)
        elif isinstance(module, AOPModules):
            assert isinstance(module, AOPModules)
            for m in module.load().asList(): context.addSetupModule(m)
        else: raise SetupError('Cannot use module %s' % module)
    
    assembly = Assembly(config or {})
    if included: assembly.calls.update(Assembly.current().calls)
    assembly = context.assemble(assembly)
    if active: assembly = activate(assembly)
    return assembly
    
def activate(assembly):
    '''
    Activates the provided assembly.
    
    @param assembly: Assembly
        The assembly to activate.
    @return: Assembly
        The same assembly for chaining purposes.
    '''
    assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
    Assembly.stack.append(assembly)
    return assembly

def processStart(assembly=None):
    '''
    Process in the assembly the start calls.
    
    @param assembly: Assembly|None
        The assembly to process the start for, if None the active assembly will be used.
    '''
    assembly = assembly or Assembly.current()
    assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
    
    unused = set(assembly.configExtern)
    unused = unused.difference(assembly.configUsed)
    if unused: log.info('Unknown configurations: %s', ', '.join(unused))
    
    calls = []
    for call in assembly.calls.values():
        if isinstance(call, CallStart):
            assert isinstance(call, CallStart)
            if call.assembly == assembly: calls.append(call)
    sortByPriorities(calls, priority=lambda call: call.priority, reverse=True)
    for call in calls: assembly.processForName(call.name)
    
def configurations(assembly=None, force=False):
    '''
    Provides the configurations for the assembly.
    
    @param assembly: Assembly|None
        The assembly to provide configurations for, if None the active assembly will be used.
    @param force: boolean
        If True will first force the configurations loading.
    '''
    if assembly is None: assembly = Assembly.current()
    assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
    if force:
        for config in assembly.configurations: assembly.processForName(config)
        # Forcing the processing of all configurations
    return assembly.trimmedConfigurations()

def deactivate():
    '''
    Deactivate the ongoing assembly.
    
    @param count: integer
        How many times to deactivate.
    '''
    assert Assembly.stack, 'No assembly available for deactivation'
    Assembly.stack.pop()
