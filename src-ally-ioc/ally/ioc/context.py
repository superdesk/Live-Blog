'''
Created on Dec 6, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the context of nodes for the IoC setup.
'''

from .indexer import Indexer
from .initializer import InitializerListener
from .node import functionFrom, SetupError, Node, toConfig
from _abcoll import Callable
from inspect import ismodule, isfunction
import logging
from .node_extra import TARGET_REPLACE, TARGET_EVENT, TARGET_CONDITION

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

class ContextIoC(Node):
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
            assert isinstance(parent, ContextIoC), 'Invalid parent %s' % parent
            if parent.doIsContext(name): raise SetupError('There is already a parent context with the name %r,'
                                                          ' please change the name of this context' % name)
        self._parentContext = parent
        self._data = {}
        
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
    
    @omni.resolver(isolation='none')
    def doIsValue(self, path):
        '''
        Checks if there is a value specified path.
        
        @param path: string
            The path to check the data for.
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        return path in self._data
        
    @omni.resolver(isolation='none')
    def doGetValue(self, path):
        '''
        Provides the values from the context node.
        
        @param path: string
            The path to get the data for.
        @return: object
            The value for the path.
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        if path not in self._data:
            assert log.debug('No value available for %r, trying to process the value', path) or True
            
            if omni.local(): source = omni.origin()
            else: source = self
            
            try:
                full = source.doFindSource(path, omni=omni.F_FIRST | omni.F_LOCAL)
                if full in self._data: return self._data[full]
            except omni.NoResultError: assert log.debug('No source available for %r' % path) or True
            
            try: return source.doProcessValue(path, omni=omni.F_FIRST | omni.F_LOCAL)
            except omni.NoResultError:
                assert log.debug('No processor available for %r' % path) or True
                return omni.CONTINUE
        return self._data[path]
    
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
        assert path not in self._data, 'The path %s already has a value' % path
        self._data[path] = value
        return True
    
    @omni.bridge
    def bridgeToParent(self):
        '''
        Provides the bridge to the parent context.
        '''
        if omni.event() == 'doFindUnused': return self._parentContext
        if not omni.resolved():
            return self._parentContext
    
    # ----------------------------------------------------------------
     
    def assemble(self):
        '''
        Assembles this context node.
        '''
        self._data[NAME_CONTEXT] = Context(self.getEntity)
        self._data[NAME_CONFIG] = Context(self.getConfig)
        
        if self._parent: self._parentContext.assemble()
        
        assembled = self.doAssemble(TARGET_REPLACE, omni=omni.F_LOCAL)
        assert log.debug('Assembled %s replacers', assembled) or True
        
        self.doAddListener(InitializerListener())
        
        assembled = self.doAssemble(TARGET_CONDITION, omni=omni.F_LOCAL)
        assert log.debug('Assembled %s conditions', assembled) or True

        return self._name
    
    def start(self):
        '''
        Starts this context node.
        '''
        assembled = self.doAssemble(TARGET_EVENT, omni=omni.F_LOCAL)
        assert log.debug('Assembled %s events', assembled) or True
        
        started = self.doStart()
        log.info('Started %s', started)
        
        if self._parent: self._parentContext.start()
        
        unused = self.doFindUnused()
        log.warn('Unused setup paths :\n\t%s', '\n\t'.join(unused))
        
        return self.getEntity(NAME_CONTEXT)
    
    # ----------------------------------------------------------------
    
    def getEntity(self, criteria):
        '''
        Resolve the entity based on a criteria.
        
        @param criteria: object
            The criteria to provide the entity based on.
        @return: object
            The entity.
        '''
        try: return omni.origin(self).doGetValue(criteria, omni=omni.F_FIRST)
        except omni.NoResultError: raise MissingError('There is no entity for %s' % criteria)
    
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
    
        try: return omni.origin(self).doGetValue(name, omni=omni.F_FIRST)
        except omni.NoResultError: raise MissingError('Cannot locate any configuration with name %r' % name)

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
    
    def __getitem__(self, criteria):
        try: return self.__resolver(criteria)
        except MissingError as e:
            raise KeyError(e)

# --------------------------------------------------------------------

def addSetupModule(context, module):
    '''
    Adds a new setup module to the context.
    
    @param context: ContextIoC
        The context to add the setup module to.
    @param module: module
        The setup module.
    '''
    assert isinstance(context, ContextIoC), 'Invalid context %s' % context
    assert ismodule(module), 'Invalid module setup %s' % module
    path = module.__name__
    
    parent = context
    assert isinstance(parent, Node)
    for name in path.split('.'):
        try: parent = parent.doFindNode(name, omni=omni.F_CHILDREN | omni.F_FIRST)
        except omni.NoResultError: parent = Node(name).setParent(parent)
    
    # Searching for module indexers
    indexers = []
    Indexer.indexersPush(module.__dict__, indexers)
    for name, value in module.__dict__.items():
        if isfunction(value) and getattr(value, '__module__', None) == path:
            if not Indexer.indexersPush(value, indexers):
                if name in NAMES_RESERVED:
                    raise SetupError('Reserved name %r for function in %r, use other name' % (name, path))
                functionFrom(value, name).setParent(parent)
    
    # Indexing into the module resource
    for indexer in indexers: indexer.index(parent)
