'''
Created on Dec 15, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the node indexers for the IoC setup.
'''

from ally.ioc.node import Configuration, toConfig, Node, SetupError
from ally.ioc.node_condition import OnlyIf, toConditionName
from ally.ioc.node_event import eventReferencedFrom, eventStartFrom
from ally.ioc.node_wire import Creator
from inspect import isfunction, isclass
import abc
from ally import omni

# --------------------------------------------------------------------

class Indexer(metaclass=abc.ABCMeta):
    '''
    Provides the ability to index the class to other objects, the purpose of this is to allow association of indexers
    with other objects.
    '''
    
    NAME_TAG = '_IoC_indexers'
    
    @classmethod
    def indexers(cls, instance):
        '''
        Provides the indexers found on the provided instance.
        
        @param instance: object
            The object to get the indexers from.
        @return: list[Indexer]|None
            The list of object indexers or None if the object has not been tagged with any indexer.
        '''
        assert instance is not None, 'An instance is expected'
        if isinstance(instance, dict): return instance.get(cls.NAME_TAG)
        return getattr(instance, cls.NAME_TAG, None)
    
    @classmethod
    def indexersPush(cls, instance, indexers):
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
        indexersInstance = cls.indexers(instance)
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
            if isinstance(instance, dict): instance[self.NAME_TAG] = indexers
            else: setattr(instance, self.NAME_TAG, indexers)
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
    
class IndexerConfiguration(Indexer):
    '''
    Provides the indexer for the configuration.
    '''
    
    def __init__(self, registry, name, value, description):
        '''
        Create the indexer.
        
        @param registry: string
            The registry to tag the configuration to.
        @param name: string
            The name of the configuration.
        @param value: object
            The value of the configuration.
        @param description: string
            The description of the configuration.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert value is not None, 'None is not a valid value'
        assert not description or isinstance(description, str), 'Invalid description %s' % description
        self._name = name
        self._value = value
        self._description = description
        self.indexerTag(registry)
    
    def index(self, parent):
        '''
        @see: Indexer.index
        '''
        Configuration(toConfig(self._name), None, True, self._value, self._description).setParent(parent)

class IndexerEventReferenced(Indexer):
    '''
    Provides the indexer for the referenced events.
    '''
    
    def __init__(self, function, event, reference):
        '''
        Create the indexer.
        
        @param function: function
            The function of the event.
        @param event: string
            The event name.
        @param reference: string
            The event reference.
        '''
        assert isfunction(function), 'Invalid function %s' % function
        assert isinstance(event, str), 'Invalid event %s' % event
        assert isinstance(reference, str), 'Invalid reference %s' % reference
        self._function = function
        self._event = event
        self._reference = reference
        self.indexerTag(function)
        
    def index(self, parent):
        '''
        @see: Indexer.index
        '''
        eventReferencedFrom(self._function, event=self._event, reference=self._reference).setParent(parent)
        
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
        except omni.NoResultError: OnlyIf(self._target, self._options).setParent(parent)
        
class IndexerCreator(Indexer):
    '''
    Provides the indexer for the creator.
    '''
    
    def __init__(self, registry, name, clazz):
        '''
        Create the indexer.
        
        @param registry: string
            The registry to tag the creator to.
        @param name: string
            The name of the creator.
        @param clazz: class
            The class to create instances of.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isclass(clazz), 'Invalid class %s' % clazz
        self._name = name
        self._clazz = clazz
        self.indexerTag(registry)
    
    def index(self, parent):
        '''
        @see: Indexer.index
        '''
        Creator(self._name, self._clazz).setParent(parent)
