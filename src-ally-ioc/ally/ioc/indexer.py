'''
Created on Dec 15, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the node indexers for the IoC setup.
'''

from .. import omni
from ..util import Attribute
from .node import Node, SetupError, functionFrom
from .node_extra import eventReferencedFrom, eventStartFrom, OnlyIf, \
    toConditionName, Replacer
from ally.ioc.node_extra import ReplacerConfigurations
from inspect import isfunction
import abc
from ally.ioc.node import isConfig, Configuration

# --------------------------------------------------------------------

ATTR_TAG = Attribute(__name__, 'indexers', list)
# Provides the attribute for tag indexers.

class Indexer(metaclass=abc.ABCMeta):
    '''
    Provides the ability to index the class to other objects, the purpose of this is to allow association of indexers
    with other objects.
    '''
    
    @staticmethod
    def indexers(instance):
        '''
        Provides the indexers found on the provided instance.
        
        @param instance: object
            The object to get the indexers from.
        @return: list[Indexer]|None
            The list of object indexers or None if the object has not been tagged with any indexer.
        '''
        assert instance is not None, 'An instance is expected'
        if isinstance(instance, dict): return ATTR_TAG.getDict(instance)
        return ATTR_TAG.get(instance, None)
    
    @staticmethod
    def indexersPush(instance, indexers):
        '''
        Pushes the indexers contained in the provided instance into the indexers list.
        
        @param instance: object
            The object to push the indexers from.
        @param indexers: list[]
            The list in which the indexers will be pushed.
        @return: boolean
            True if any relevant indexers have been pushed, False if no or none relevant indexers have been added.
        '''
        assert isinstance(indexers, list), 'Invalid indexers %s' % indexers
        indexersInstance = Indexer.indexers(instance)
        if indexersInstance:
            relevant = False
            for indexer in indexersInstance:
                assert isinstance(indexer, Indexer), 'Invalid indexer %s' % indexer
                relevant |= indexer.indexerAdd(indexers)
            return relevant
        return False
    
    def indexerTag(self, instance):
        '''
        Tags this indexer on the provided instance.
        
        @param instance: object
            The object to tag the indexers to.
        '''
        indexers = self.indexers(instance)
        if indexers is None:
            indexers = []
            if isinstance(instance, dict): ATTR_TAG.setDict(instance, indexers)
            else: ATTR_TAG.set(instance, indexers)
        self.indexerAdd(indexers)
        
    def indexerAdd(self, indexers):
        '''
        Add this indexer to the provided list of indexers.
        
        @param indexers: list[]
            The list in which the indexer will be added.
        @return: boolean
            True if a relevant indexer has been added, False if a none relevant indexer has been added.
        '''
        assert isinstance(indexers, list), 'Invalid indexers %s' % indexers
        indexers.append(self)
        return True
        
    @abc.abstractclassmethod
    def index(self, parent):
        '''
        This method is called whenever the indexer is required to index him self into the provided parent.
        
        @param parent: object
            The parent to index on.
        '''

# --------------------------------------------------------------------

class IndexerEventReferenced(Indexer):
    '''
    Provides the indexer for the referenced events.
    '''
    
    def __init__(self, function, event, reference, multiple=None):
        '''
        Create the indexer.
        
        @param function: function
            The function of the event.
        @param event: string
            The event name.
        @param reference: string
            The event reference.
        @param multiple: boolean|None
            True indicates that the event is allowed to be handled multiple times, False the event should be handled just
            once and None allows the event handler to provide a default behavior based on the reference
            (True for entities, False for configurations)
        '''
        assert isfunction(function), 'Invalid function %s' % function
        assert isinstance(event, str), 'Invalid event %s' % event
        assert isinstance(reference, str), 'Invalid reference %s' % reference
        assert multiple is None or isinstance(multiple, bool), 'Invalid multiple flag %s' % multiple
        self._function = function
        self._event = event
        self._reference = reference
        self._multiple = multiple
        self.indexerTag(function)
        
    def index(self, parent):
        '''
        @see: Indexer.index
        '''
        eventReferencedFrom(self._function, self._event, None, self._reference, self._multiple).setParent(parent)
        
class IndexerEventStart(Indexer):
    '''
    Provides the indexer for the start events.
    '''
    
    def __init__(self, function):
        '''
        Create the indexer.
        
        @param function: function
            The function of the event.
        '''
        assert isfunction(function), 'Invalid function %s' % function
        self._function = function
        self.indexerTag(function)
        
    def index(self, parent):
        '''
        @see: Indexer.index
        '''
        eventStartFrom(self._function).setParent(parent)

class IndexerOnlyIf(Indexer):
    '''
    Provides the indexer for the only if condition.
    '''
    
    def __init__(self, registry, target, options):
        '''
        Create the indexer.
        
        @param registry: string
            The registry to tag the configuration to.
        @param target: string
            The target of the condition.
        @param options: dictionary{string, object}
            The condition options.
        '''
        assert isinstance(target, str), 'Invalid target %s' % target
        assert isinstance(options, dict), 'Invalid options %s' % options
        self._target = target
        self._options = options
        self.indexerTag(registry)
    
    def indexerAdd(self, indexers):
        '''
        @see: Indexer.indexerAdd
        '''
        super().indexerAdd(indexers)
        return False # We return false because the condition is not an actual relevant structure node.
    
    def index(self, parent):
        '''
        @see: Indexer.index
        '''
        assert isinstance(parent, Node), 'Invalid parent node %s' % parent
        try:
            node = parent.doFindNode(toConditionName(self._target, OnlyIf), omni=omni.F_CHILDREN | omni.F_FIRST)
            if not isinstance(node, OnlyIf):
                raise SetupError('There is a child node %s where the only if condition suppose to be.' % node)
            assert isinstance(node, OnlyIf)
            node.addOptions(self._options)
        except omni.NoResultError: node = OnlyIf(self._target, self._options).setParent(parent)
        for name, value in self._options.items():
            if isConfig(name): Configuration(name, None if value is None else value.__class__ , False).setParent(node)

class IndexerReplacerFunction(Indexer):
    '''
    Provides the indexer that replaces a target with a function.
    '''
    
    def __init__(self, function, target):
        '''
        Create the indexer.
        
        @param function: function
            The replacer function.
        @param target: string
            The target name.
        '''
        assert isfunction(function), 'Invalid function %s' % function
        assert isinstance(target, str), 'Invalid target %s' % target
        self._function = function
        self._target = target
        self.indexerTag(function)
        
    def index(self, parent):
        '''
        @see: Indexer.index
        '''
        Replacer(self._function.__name__, functionFrom(self._function, self._target)).setParent(parent)

    
class IndexerConfigurations(Indexer):
    '''
    Provides the indexer for setting configurations.
    '''
    
    @staticmethod
    def place(registry, configurations):
        '''
        Places the provided configurations to the registry.
        
        @param registry: string
            The registry to tag the configuration to.
        @param configurations: dictionary{string, object}
            The configurations dictionary.
        '''
        assert isinstance(configurations, dict), 'Invalid configurations %s' % configurations
        if __debug__:
            for name in configurations: assert isinstance(name, str), 'Invalid configuration name %s' % name
        indexers, indexer = Indexer.indexers(registry), None
        
        if indexers:
            for ind in indexers:
                if isinstance(ind, IndexerConfigurations):
                    indexer = ind
                    break
            
        if not indexer:
            indexer = IndexerConfigurations()
            indexer.indexerTag(registry)

        indexer._configurations.update(configurations)
    
    def __init__(self):
        '''
        Create the indexer.
        '''
        self._configurations = {}
    
    def index(self, parent):
        '''
        @see: Indexer.index
        '''
        ReplacerConfigurations(self._configurations).setParent(parent)
