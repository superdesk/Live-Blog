'''
Created on Jul 27, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides basic encode implementations. 
'''

from ally.core.spec.encdec.exploit import IResolve
from ally.core.spec.encdec.render import IRender
from ally.core.spec.resources import Normalizer
from collections import Iterable, OrderedDict

# --------------------------------------------------------------------

class EncodeObject:
    '''
    Exploit for object encoding.
    '''
    __slots__ = ('name', 'getter', 'properties')

    def __init__(self, name, getter=None):
        '''
        Create a encode exploit for a model.
        
        @param name: string
            The name of the model to encode.
        @param getter: callable(object) -> object|None
            The getter used to get the object from the value object.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        self.name = name
        self.getter = getter
        self.properties = OrderedDict()

    def __call__(self, value, render, normalizer, name=None, **data):
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert name is None or isinstance(name, str), 'Invalid name %s' % name

        if self.getter: value = self.getter(value)
        if value is None: return

        render.objectStart(normalizer.normalize(name or self.name))
        data.update(value=value, render=render, normalizer=normalizer)
        for nameProp, exploitProp in self.properties.items(): exploitProp(name=nameProp, **data)

        render.objectEnd()

class EncodeCollection:
    '''
    Exploit for collection encoding.
    '''
    __slots__ = ('name', 'exploitItem', 'getter')

    def __init__(self, name, exploitItem, getter=None):
        '''
        Create a encode exploit for a collection.
        
        @param name: string
            The name to use for the collection.
        @param exploitItem: callable(**data)
            The exploit to be used for the item encoding.
        @param getter: callable(object) -> object|None
            The getter used to get the model collection from the value object.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert callable(exploitItem), 'Invalid exploit %s' % exploitItem
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        self.name = name
        self.exploitItem = exploitItem
        self.getter = getter

    def __call__(self, value, normalizer, render, resolve, name=None, **data):
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(resolve, IResolve), 'Invalid resolve %s' % resolve

        if self.getter: value = self.getter(value)
        if value is None: return
        assert isinstance(value, Iterable), 'Invalid value %s' % value

        data.update(normalizer=normalizer, render=render, resolve=resolve)
        render.collectionStart(normalizer.normalize(name or self.name))
        resolve.queueBatch(self.exploitItem, (dict(data, value=item) for item in value))
        resolve.queue(self.finalize, render=render)

    def finalize(self, render, **data):
        assert isinstance(render, IRender), 'Invalid render %s' % render

        render.collectionEnd()
