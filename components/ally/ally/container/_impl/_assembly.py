'''
Created on Jan 8, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup assembly implementations for the IoC module.
'''

from ..error import SetupError, ConfigError
from ..impl.config import Config
from collections import deque
from inspect import ismodule
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Setup(metaclass=abc.ABCMeta):
    '''
    The setup entity. This class provides the means of indexing setup Callable objects.
    '''

    priority_index = 1
    # Provides the indexing priority for the setup.
    priority_assemble = 1
    # Provides the assemble priority for the setup.

    def index(self, assembly):
        '''
        Indexes the call of the setup and other data.
        
        @param assembly: Assembly
            The assembly to index on.
        '''

    def assemble(self, assembly):
        '''
        Assemble the calls map and also add the call starts. This method will be invoked after all index methods have
        been finalized.
        
        @param assembly: Assembly
            The assembly to assemble additional behavior on.
        '''
    
    @abc.abstractmethod
    def __str__(self):
        '''
        Representation for setup function.
        '''
        
# --------------------------------------------------------------------

class Assembly:
    '''
    Provides the assembly data.
    '''

    stack = []
    # The current assemblies stack.

    @classmethod
    def current(cls):
        '''
        Provides the current assembly.
        
        @return: Assembly
            The current assembly.
        @raise SetupError: if there is no current assembly.
        '''
        if not cls.stack: raise SetupError('There is no active assembly to process on')
        return cls.stack[-1]

    @classmethod
    def process(cls, name):
        '''
        Process the specified name into the current active context.
        
        @param name: string
            The name to be processed.
        '''
        ass = cls.current()
        assert isinstance(ass, Assembly), 'Invalid assembly %s' % ass
        return ass.processForName(name)

    def __init__(self, configExtern):
        '''
        Construct the assembly.
        
        @param configExtern: dictionary{string, object}
            The external configurations values to be used in the context.
        @ivar configUsed: set{string}
            A set containing the used configurations names from the external configurations.
        @ivar configurations: dictionary{string:Config}
            A dictionary of the assembly configurations, the key is the configuration name and the value is a
            Config object.
        @ivar calls: dictionary{string, Callable}
            A dictionary containing as a key the name of the call to be resolved and as a value the Callable that will
            resolve the name. The Callable will not take any argument.
        @ivar callsOfValue: dictionary{intege:list[Callable]}
            A dictionary containing the calls for a value, the value id is used as a key.
        @ivar called: set[string]
            A set of the called calls in this assembly.
            
        @ivar _processing: deque(string)
            Used internally for tracking the processing chain.
        '''
        assert isinstance(configExtern, dict), 'Invalid external configurations %s' % configExtern
        self.configExtern = configExtern
        self.configUsed = set()
        self.configurations = {}
        self.calls = {}
        self.callsOfValue = {}
        self.called = set()

        self._processing = deque()

    def trimmedConfigurations(self):
        '''
        Provides a configurations dictionary that has the configuration names trimmed.
        
        @return:  dictionary[string, Config]
            A dictionary of the assembly configurations, the key is the configuration name and the value 
            is a Config object.
        '''
        def expand(name, sub):
            ''' Used for expanding configuration names'''
            if sub: root = name[:-len(sub)]
            else: root = name
            if not root: return name
            if root[-1] == '.': root = root[:-1]
            k = root.rfind('.')
            if k < 0: return name
            if sub: return root[k + 1:] + '.' + sub
            return root[k + 1:]

        configs, expanded = {}, set()
        for name, config in self.configurations.items():
            assert isinstance(config, Config), 'Invalid configuration %s' % config
            sname = name[len(config.group) + 1:]
            other = configs.pop(sname, None)
            while other or sname in expanded:
                if other:
                    assert isinstance(other, Config)
                    configs[expand(other.name, sname)] = other
                    expanded.add(sname)
                sname = expand(name, sname)
                other = configs.pop(sname, None)
            configs[sname] = config
        return configs
    
    def fetchForName(self, name):
        '''
        Fetch the call with the specified name.
        
        @param name: string
            The name of the call to be fetched.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        call = self.calls.get(name)
        if not call: raise SetupError('No IoC resource for name \'%s\', possible reasons:\n\t- the setup function you '
        'are calling is not registered in the current assembly\n\t- you have added an \'after\' or \'before\' event to '
        'a setup function that is from a different assembly\n\t  and when the event is triggered the setup function assembly '
        'is no longer available' % name)
        if not callable(call): raise SetupError('Invalid call %s for name \'%s\'' % (call, name))
        return call

    def processForName(self, name):
        '''
        Process the specified name into this assembly.
        
        @param name: string
            The name to be processed.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        self._processing.append(name)
        try: value = self.fetchForName(name)()
        except (SetupError, ConfigError, SystemExit): raise
        except: raise SetupError('Exception occurred for %r in processing chain \'%s\'' % 
                                 (name, ', '.join(self._processing)))
        self._processing.pop()
        return value

class Context:
    '''
    Provides the context of the setup functions and setup calls.
    '''

    def __init__(self):
        '''
        Construct the context.
        '''
        self._modules = []

    def addSetupModule(self, module):
        '''
        Adds a new setup module to the context.
        
        @param module: module
            The setup module.
        '''
        assert ismodule(module), 'Invalid module setup %s' % module
        try: module.__ally_setups__
        except AttributeError: log.info('No setup found in %s', module)
        else:
            self._modules.append(module)
            self._modules.sort(key=lambda module: module.__name__)

    def assemble(self, assembly):
        '''
        Assembles into the provided assembly this context.
        
        @param assembly: Assembly
            The assembly to assemble the context into.
        @return: Assembly
            The assembled assembly.
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        
        setups = deque()
        for module in self._modules: setups.extend(module.__ally_setups__) 
        
        for setup in sorted(setups, key=lambda setup: setup.priority_index):
            assert isinstance(setup, Setup), 'Invalid setup %s' % setup
            setup.index(assembly)

        for setup in sorted(setups, key=lambda setup: setup.priority_assemble):
            setup.assemble(assembly)

        return assembly
