'''
Created on May 23, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides static functions support for exploit processing. 
'''

# --------------------------------------------------------------------

SAMPLE = object() # Marker used to instruct the encoders to provide a sample.

# --------------------------------------------------------------------

def getSame(obj):
    '''
    Function that just returns the same value received.
    '''
    return obj

# --------------------------------------------------------------------

def getterOnDict(key):
    '''
    Create a getter on a dictionary for the provided key.
    
    @param key: object
        The key in the dictionary to get the query for.
    '''
    def getter(obj):
        assert isinstance(obj, dict), 'Invalid dictionary %s' % obj
        return obj.get(key)
    return getter

def getterOnObj(attribute):
    '''
    Create a getter on a object attribute.
    
    @param attribute: string
        The attribute name to get the value for.
    '''
    assert isinstance(attribute, str), 'Invalid attribute %s' % attribute

    def getter(obj):
        assert obj is not None, 'An object is required'
        return getattr(obj, attribute)
    return getter

def getterOnObjIfIn(attribute, checkIn):
    '''
    Create a getter for the attribute. If the provided object is None or the checkIn is no validated like
    'checkIn in obj' on the object than the getter will return None.
    
    @param attribute: string
        The attribute name to get the value for.
    @param checkIn: object
        The object to check if in the object.
    '''
    assert checkIn is not None, 'A check in object is required'

    def getter(obj):
        if checkIn in obj: return getattr(obj, attribute)
    return getter

def getterChain(*getters):
    '''
    Create a getter chain, this means that the first getter will be invoked and the object returned will passed on as 
    an object to the next getter so fort and so on. If one getter return None then the chain stops.
    
    @param getters: attributes[callable(object)]
        The getters to be invoked in a chain.
    '''
    assert getters, 'At least a getter is required'
    if __debug__:
        for getter in getters: assert callable(getter), 'Invalid getter %s' % getter

    def getter(obj):
        for getter in getters:
            obj = getter(obj)
            if obj is None: break
        return obj
    return getter

def setterOnDict(key):
    '''
    Create a setter on a dictionary for the provided key.
    
    @param key: string
        The key in the dictionary to set the value.
    '''
    def setter(obj, value):
        assert isinstance(obj, dict), 'Invalid dictionary %s' % obj
        obj[key] = value
    return setter

def setterOnObj(attribute):
    '''
    Create a setter on a object attribute.
    
    @param attribute: string
        The attribute name to set the value for.
    '''
    assert isinstance(attribute, str), 'Invalid attribute %s' % attribute

    def setter(obj, value):
        assert obj is not None, 'An object is required'
        setattr(obj, attribute, value)
    return setter

def setterToOthers(*setters):
    '''
    Create a setter that will dispatch to a list of other setters.
    
    @param setters: arguments[callable]
        The setters to delegate the set to.
    '''
    assert setters, 'At least a setter is required'
    if __debug__:
        for setter in setters:
            assert callable(setter), 'Invalid setter %s' % setter

    def setter(obj, value):
        for setter in setters: setter(obj, value)
    return setter

def setterWithGetter(getter, setter):
    '''
    Create a setter that will first call the getter on the object than set the value on the returned object.
    
    @param getter: callable(object)
        The getter to call with the object before the setter.
    @param setter: callable(object)
        The setter to be used.
    '''
    assert callable(getter), 'Invalid getter %s' % getter
    assert callable(setter), 'Invalid setter %s' % setter

    def sett(obj, value):
        setter(getter(obj), value)
    return sett

def obtainOnDict(key, creator):
    '''
    Create an obtain object on a dictionary for the provided key. Obtaining means that if there is not value
    for the key one will be created and assigned.
    
    @param key: string
        The key in the dictionary to obtain the value.
    @param creator: callable()
        The creator to use in generating the object, has to take no arguments.
    '''
    assert callable(creator), 'Invalid creator %s' % creator

    def obtain(obj):
        assert isinstance(obj, dict), 'Invalid dictionary %s' % obj
        value = obj.get(key)
        if value is None: obj[key] = value = creator()
        assert value is not None, 'No value provided by creator %s' % creator
        return value
    return obtain

def obtainOnObj(attribute, creator):
    '''
    Create an obtain object on another object for the provided attribute. Obtaining means that if there is not value
    for the attribute one will be created and assigned.
    
    @param attribute: string
        The attribute in the object to obtain the value.
    @param creator: callable()
        The creator to use in generating the object, has to take no arguments.
    '''
    assert callable(creator), 'Invalid creator %s' % creator

    def obtain(obj):
        assert obj is not None, 'An object is required'
        value = getattr(obj, attribute, None)
        if value is None:
            value = creator()
            assert value is not None, 'No value provided by creator %s' % creator
            setattr(obj, attribute, value)
        return value
    return obtain
