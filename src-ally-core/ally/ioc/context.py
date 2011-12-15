'''
Created on Dec 6, 2011

@author: chupy
'''

from .. import omni
from .indexer import Indexer
from .node import functionFrom, SetupError, Node, toConfig
from _abcoll import Callable
from inspect import ismodule, isfunction
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

NAME_CONTEXT = 'ctx'
# The name of the context entity.
NAME_CONFIG = 'cfg'
# The name of the context entity.
NAMES_RESERVED = (NAME_CONTEXT, NAME_CONFIG)
# Contains the reserved names.

# --------------------------------------------------------------------
    
class MissingError(Exception):
    '''
    Exception thrown when a criteria is missing.
    '''

# --------------------------------------------------------------------

class ContextIoC:
    '''
    Provides the context for the IoC setup modules.
    '''
    
    def __init__(self, name, parent=None):
        '''
        Construct the IoC context.
        
        @param name: string
            The context name.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        if parent:
            assert isinstance(parent, ContextIoC), 'Invalid parent %s' % parent
            self._root = ContextNode(name, parent._root)
        else: self._root = ContextNode(name)
        
    def addConfigurations(self, configurations):
        '''
        Adds configurations for the context.
        
        @param configurations: dictionary{string, object} 
        '''
        assert isinstance(configurations, dict), 'Invalid configurations dictionary %s' % configurations
        if __debug__:
            for name in configurations: assert isinstance(name, str), 'Invalid configuration name %s' % name
        self._root.data.update({toConfig(name): value for name, value in configurations.items()})
        
    def putConfigurations(self, configurations):
        '''
        Adds the configurations for the context only if they are not present.
        
        @param configurations: dictionary{string, object} 
        '''
        assert isinstance(configurations, dict), 'Invalid configurations dictionary %s' % configurations
        for name, value in configurations.items():
            assert isinstance(name, str), 'Invalid configuration name %s' % name
            name = toConfig(name)
            if name not in self._root.data: self._root.data[name] = value
        
    def addSetupModule(self, module):
        '''
        Adds a new setup module to the context.
        
        @param module: module
            The setup module.
        '''
        assert ismodule(module), 'Invalid module setup %s' % module
        path = module.__name__
        
        parent = self._root
        assert isinstance(parent, Node)
        for name in path.split('.'):
            try: parent = parent.doFindNode(name, omni=omni.F_CHILDREN | omni.F_FIRST)
            except omni.NoResultError: parent = Node(name).setParent(parent)
        
        # Searching for module indexers
        indexers = []
        Indexer.indexersPush(module, indexers)
        for name, value in module.__dict__.items():
            if isfunction(value) and getattr(value, '__module__', None) == path:
                if not Indexer.indexersPush(value, indexers):
                    if name in NAMES_RESERVED:
                        raise SetupError('Reserved name %r for function in %r, use other name' % (name, path))
                    functionFrom(value, name).setParent(parent)
        
        # Indexing into the module resource
        for indexer in indexers: indexer.index(parent)
                
    def assemble(self):
        '''
        Assembles this IoC context resolving all beans and dependencies that have been added to it.
        
        @return: Context
            The assembled beans context.
        '''
        self._root.doAssemble()
        self._root.doStart()
    
        unused = self._root.doFindUnused()
        print('\n'.join(unused))
        
        return self._root.data[NAME_CONTEXT]

# --------------------------------------------------------------------

class ContextNode(Node):
    '''
    Provides the context node.
    '''
    
    def __init__(self, name, parent=None):
        '''
        @see: Node.__init__
        
        @param parent: ContextNode|None
            The context node parent.
        '''
        Node.__init__(self, name)
        if parent:
            assert isinstance(parent, ContextNode), 'Invalid parent %s' % parent
            if parent.doIsContext(name): raise SetupError('There is already a parent context with the name %r,'
                                                          ' please change the name of this context' % name)
        self._parentContext = parent
        self.data = {}
    
    @omni.resolver   
    def doIsContext(self, name):
        '''
        Checks if there is a context with the provided name.
        
        @param name: string
            The context name to check.
        @return: boolean
            True if the context checks the name, false otherwise.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        if self._name == name: return True
        return omni.CONTINUE
    
    @omni.resolver(isolation='resolver')
    def doFindSource(self, *criteria):
        '''
        Finds the node that recognizes the criteria and has a data source to deliver.
        
        @param criteria: object
            The criteria used to identify the node.
        @return: string
            The path of the source.
        '''
        for path in criteria:
            if isinstance(path, str) and path in self.data: return path
        return omni.CONTINUE
    
    @omni.resolver
    def doFindConfiguration(self, *criteria):
        '''
        Finds the configurations with values for the provided criteria.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the configuration.
        '''
        for path in criteria:
            if isinstance(path, str) and path in self.data: return path
        return omni.CONTINUE
    
    @omni.resolver(isolation='none')
    def doIsValue(self, path):
        '''
        Checks if there is a value specified path.
        
        @param path: string
            The path to check the data for.
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        return path in self.data
        
    @omni.resolver(isolation='none')
    def doGetValue(self, path):
        '''
        Provides the values from the context node.
        
        @param path: string
            The path to get the data for.
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        if path not in self.data:
            log.debug('No value available for %r, trying to process the value', path)
            
            if omni.local(): source = omni.origin()
            else: source = self
            
            try:
                full = source.doFindSource(path, omni=omni.F_FIRST | omni.F_LOCAL)
                if full in self.data: return self.data[full]
            except omni.NoResultError: log.debug('No source available for %r' % path)
            
            try: return source.doProcessValue(path, omni=omni.F_FIRST | omni.F_LOCAL)
            except omni.NoResultError:
                log.debug('No processor available for %r' % path)
                return omni.CONTINUE
        return self.data[path]
    
    @omni.resolver(isolation='none')
    def doSetValue(self, path, value):
        '''
        Sets the values to the context node.
        
        @param path: string
            The path under which the data will be registered.
        @param value: object
            The value to be registered.
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        assert path not in self.data, 'The path %s already has a value' % path
        self.data[path] = value
        return True
    
    @omni.resolver
    def doAssemble(self):
        '''
        Assembles this context node.
        '''
        self.data[NAME_CONTEXT] = Context(self.getEntity)
        self.data[NAME_CONFIG] = Context(self.getConfig)
        if self._parent: self._parentContext.doAssemble()
        return omni.CONTINUE # We just let others also assemble, especially the bridged ones.
    
    @omni.bridge
    def bridgeToParent(self):
        '''
        Provides the bridge to the parent context.
        '''
        if omni.event() == 'doFindUnused': return self._parentContext
        if not omni.resolved():
            return self._parentContext
        
    def getEntity(self, criteria):
        '''
        Resolve the entity based on a criteria.
        
        @param criteria: object
            The criteria to provide the entity based on.
        @return: object
            The entity.
        '''
        try: path = omni.origin(self).doFindSource(criteria, omni=omni.F_FIRST)
        except omni.NoResultError: raise MissingError('There is no value for %s' % criteria)
        return omni.origin(self).doGetValue(path, omni=omni.F_FIRST)
    
    def getConfig(self, name):
        '''
        Resolve the configuration based on the name.
        
        @param name: string
            The name to get the configuration for.
        @return: object
            The configuration value.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        name = toConfig(name)
    
        try: path = omni.origin(self).doFindSource(name, omni=omni.F_FIRST)
        except omni.NoResultError: raise MissingError('Cannot locate any configuration with name %r' % name)
        return omni.origin(self).doGetValue(path, omni=omni.F_FIRST)

class Context:
    '''
    Support class that provides the context entity data.
    '''
    
    __slots__ = ['__resolver']
    
    def __init__(self, resolver):
        assert isinstance(resolver, Callable), 'Invalid entity resolver %s' % resolver
        self.__resolver = resolver
        
    def __getattr__(self, name):
        try: return self.__resolver(name)
        except MissingError as e:
            raise AttributeError(e)
    
    def __getitem__(self, name):
        try: return self.__resolver(name)
        except MissingError as e:
            raise KeyError(e)

