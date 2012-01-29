'''
Created on Jan 27, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the data meta support. 
'''

from ally.api.type import Type

# --------------------------------------------------------------------

returnSame = lambda obj: obj
# Function that just returns the same value received.

# --------------------------------------------------------------------

class Object:
    '''
    Provides the object meta.
    '''
    
    def __init__(self, getObject=returnSame, properties=None):
        '''
        Construct the object meta.

        @param getObject: Callable(object)
            A callable that takes as an argument the object to extract this meta object instance.
        @param properties: dictionary{string, object meta}|None
            The object properties.
        '''
        assert callable(getObject), 'Invalid get object callable %s' % getObject
        assert properties is None or isinstance(properties, dict), 'Invalid properties %s' % properties
        self.getObject = getObject
        self.properties = properties or {}
    
class List:
    '''
    Provides the list meta.
    '''
    
    def __init__(self, itemMeta, getItems=returnSame):
        '''
        Construct the list meta.

        @param itemMeta: Object|Path
            The item object.
        @param getItems: Callable(object)
            A callable that takes as an argument the object to extract this meta list instance.
        '''
        assert callable(getItems), 'Invalid get items callable %s' % getItems
        assert isinstance(itemMeta, (Object, Link)), 'Invalid meta object %s' % itemMeta
        self.getItems = getItems
        self.itemMeta = itemMeta
    
class Value:
    '''
    Provides the value meta.
    '''
    
    def __init__(self, type, getValue=returnSame):
        '''
        Construct the list meta.
        
        @param type: Type
            The value type.
        @param getValue: Callable(object)
            A callable that takes as an argument the object to extract this meta value instance.
        '''
        assert isinstance(type, Type), 'Invalid value type %s' % type
        assert callable(getValue), 'Invalid get value callable %s' % getValue
        self.type = type
        self.getValue = getValue
    
class Link:
    '''
    Provides the link meta.
    '''
    
    def __init__(self, getLink=returnSame):
        '''
        Construct the link meta.
        
        @param getLink: Callable(object)
            A callable that takes as an argument the object to extract the path.
        '''
        assert callable(getLink), 'Invalid get link callable %s' % getLink
        self.getLink = getLink

class ValueLink(Value, Link):
    '''
    Provides the value and link meta.
    '''
    
    def __init__(self, type, getValue=returnSame, getLink=returnSame):
        '''
        Construct the value and link meta.

        @param getLink: Callable(object)
            A callable that takes as an argument the object to extract the path.
        @param type: Type
            The value type.
        @param getValue: Callable(object)
            A callable that takes as an argument the object to extract this meta value instance.
        '''
        Value.__init__(self, type, getValue)
        Link.__init__(self, getLink)
        
