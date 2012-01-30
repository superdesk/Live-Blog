'''
Created on Jan 27, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the data meta support. 
'''

from ally.api.operator import Model
from ally.api.type import Type, TypeProperty, TypeModel
from ally.core.spec.resources import Path
from ally.support.util import immutable

# --------------------------------------------------------------------

returnSame = lambda obj: obj
# Function that just returns the same value received.

# --------------------------------------------------------------------

@immutable
class MetaModel(dict):
    '''
    Provides the meta model object.
    '''
    
    __slots__ = ('model', 'getModel')
    __immutable__ = ('model', 'getModel')
    
    def __init__(self, model, getModel, *args, **keyargs):
        '''
        Construct the object meta.

        @param getModel: Callable(object)
            A callable that takes as an argument the object to extract the model instance.
        @param metaProperties: dictionary{string, object meta}|None
            The meta properties.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert callable(getModel), 'Invalid get model callable %s' % getModel
        self.model = model
        self.getModel = getModel
        super().__init__(*args, **keyargs)
        
    def clone(self):
        '''
        Clone this meta.
        '''
        clone = MetaModel(self.model, self.getModel)
        clone.update({name:meta.clone() for name, meta in self.metaProperties.items()})
        return clone

@immutable  
class MetaList:
    '''
    Provides the list meta.
    '''
    
    __slots__ = ('metaItem', 'getItems')
    __immutable__ = ('metaItem', 'getItems')
    
    def __init__(self, metaItem, getItems):
        '''
        Construct the list meta.

        @param metaItem: MetaModel|MetaLink
            The meta item.
        @param getItems: Callable(object)
            A callable that takes as an argument the object to extract this meta list instance.
        '''
        assert isinstance(metaItem, (MetaModel, MetaLink)), 'Invalid meta item %s' % metaItem
        assert callable(getItems), 'Invalid get items callable %s' % getItems
        self.metaItem = metaItem
        self.getItems = getItems
        
    def clone(self):
        '''
        Clone this meta.
        '''
        return self

@immutable
class MetaLink:
    '''
    Provides the link meta.
    '''
    
    __slots__ = ('getLink',)
    __immutable__ = ('getLink',)
    
    def __init__(self, getLink):
        '''
        Construct the link meta.
        
        @param getLink: Callable(object)
            A callable that takes as an argument the object to extract the path.
        '''
        assert callable(getLink), 'Invalid get link callable %s' % getLink
        self.getLink = getLink
        
    def clone(self):
        '''
        Clone this meta.
        '''
        return self

@immutable
class MetaValue:
    '''
    Provides the value meta.
    '''
    
    __slots__ = ('type', 'getValue', 'metaLink')
    __immutable__ = ('type', 'getValue', 'metaLink')
    
    def __init__(self, type, getValue, metaLink=None):
        '''
        Construct the list meta.
        
        @param type: Type
            The value type.
        @param getValue: Callable(object)
            A callable that takes as an argument the object to extract this meta value instance.
        @param metaLink: MetaLink|None
            The meta link of the value or None.
        '''
        assert isinstance(type, Type), 'Invalid value type %s' % type
        assert callable(getValue), 'Invalid get value callable %s' % getValue
        assert metaLink is None or isinstance(metaLink, MetaLink), 'Invalid meta link %s' % metaLink
        self.type = type
        self.getValue = getValue
        self.metaLink = metaLink

    def clone(self):
        '''
        Clone this meta.
        '''
        return self

# --------------------------------------------------------------------

class MetaPath(MetaLink):
    '''
    Provides the link on path meta.
    '''
    
    __slots__ = ('type', 'path', 'getValue')
    __immutable__ = ('type', 'path', 'getValue')
    
    def __init__(self, path, type, getValue):
        '''
        Construct the update path callable.
        
        @param path: Path
            The path to be updated and returned.
        @param type: TypeProperty|TypeModel
            The type of the object to be updated.
        @param getValue: Callable(object)
            A callable that takes as an argument the object to extract the value for the path.
        '''
        assert isinstance(path, Path), 'Invalid path %s' % path
        assert isinstance(type, (TypeProperty, TypeModel)), 'Invalid type %s' % type
        assert callable(getValue), 'Invalid get value callable %s' % getValue
        self.type = type
        self.path = path
        self.getValue = getValue
        
    def getLink(self, obj):
        '''
        Provides the updated path.
        
        @return: Path
            The updated path.
        '''
        path = self.path.clone()
        assert isinstance(path, Path)
        path.update(self.getValue(obj), self.type)
        assert path.isValid(), 'The updated path %s is not valid' % self.path
        return path
