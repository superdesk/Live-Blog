'''
Created on Jun 27, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides exploits for transforming to objects. 
'''

from ally.api.type import Type
from ally.core.spec.resources import Converter, Normalizer
from ally.design.exploit import NORMAL, Exploit

# --------------------------------------------------------------------

def locatorNormalized(status=NORMAL):
    '''
    The locator that provides the search based on a normalized path.
    
    @param status: integer
        The status considered valid for the exploit entries searched by this locator.
    '''
    assert isinstance(status, int), 'Invalid status %s' % status

    def locator(*path, exploit, normalizer, **data):
        assert isinstance(exploit, Exploit), 'Invalid exploit node %s' % exploit
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer

        children = exploit.children
        for key in path:
            assert isinstance(key, str), 'Invalid path key %s' % key

            for exploitKey, exploit in children.items():
                if isinstance(exploitKey, str) and normalizer.normalize(exploitKey) == key: break
            else: return
            if not (exploit.status & status): return # The status doesn't match
            children = exploit.children

        return exploit
    return locator

def locatorSplit(delegateLocator, separator):
    '''
    Create a locator that will split the string path based on the separator. No action will be taken if the path is not a
    single string and will just be passed along to the wrapped locator.
    
    @param delegateLocator: callable(*path, exploit, **data) -> Exploit|None
        The locator call to delegate with the splited path.
    @param separator: string
        The separator to be used for converting the string identifier.
    '''
    assert callable(delegateLocator), 'Invalid locator delegate %s' % delegateLocator
    assert isinstance(separator, str), 'Invalid separator %s' % separator

    def locator(*path, **data):
        if len(path) == 1 and isinstance(path[0], str): path = path[0].split(separator)

        return delegateLocator(*path, **data)
    return locator

# --------------------------------------------------------------------

def targetGetter(delegate, getter):
    '''
    Exploit that actually just uses a getter to fetch a value from the target object and pass it to the exploit
    delegate. If the value fetched is None then this exploit will return False and not delegate to the delegated exploit.
    
    @param delegate: callable(**data)
        The exploit call to delegate with the obtained value.
    @param getter: callable(object)
        The getter used to fetch the value from the target object.
    '''
    assert callable(delegate), 'Invalid delegate %s' % delegate
    assert callable(getter), 'Invalid getter %s' % getter

    def exploit(target, **data):
        target = getter(target)
        if target is None: return False
        return delegate(target=target, **data)
    return exploit

def targetSetConvertedValue(setter, type):
    '''
    Exploit that processes the string value to a value based on the assigned type by using the call converter and set 
    it to the target object.
    
    @param setter: callable(object, object)
        The setter used to set the value to the target object.
    @param type: Type
        The type represented by the decoder.
    '''
    assert callable(setter), 'Invalid setter %s' % setter
    assert isinstance(type, Type), 'Invalid type %s' % type

    def exploit(target, value, converter, **data):
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter

        if not isinstance(value, str): return False
        # If the value is not a string then is not valid
        try: value = converter.asValue(value, type)
        except ValueError: return False

        setter(target, value)
        return True
    return exploit

def targetSetValue(setter):
    '''
    Exploit that sets the received value directly on the target using the provided setter.
    
    @param setter: callable(object, object)
        The setter used to set the value to the target object.
    '''
    assert callable(setter), 'Invalid setter %s' % setter

    def exploit(target, value, **data):
        setter(target, value)
        return True
    return exploit

# --------------------------------------------------------------------

def valueListExplode(delegate):
    '''
    Exploit that explodes the value list or tuple into single values that will be passes on to the delegated exploit.
    If the value is not a list or a tuple will be passed as it is to the delegated exploit.
    
    @param delegate: callable
        The exploit call to delegate with the obtained value.
    '''
    assert callable(delegate), 'Invalid delegate %s' % delegate

    def exploit(value, **data):
        if isinstance(value, (list, tuple)):
            for item in value:
                if not delegate(value=item, **data): return False
            return True
        return delegate(value=value, **data)
    return exploit

def valueSplit(delegate, splitValues, normalizeValue=None):
    '''
    Exploit that splits a string value into a list of values and pass the values to the contained service, if the 
    received value is not a string then it will be delegated to the contained service as it is. 
    
    @param delegate: callable(**data)
        The exploit call to delegate with the obtained list.
    @param splitValues: complied regex
        The regex to use in spliting the values.
    @param normalizeValue: complied regex|None
        The regex to use in normalizing the splited values, if None no normalization will occur.
    '''
    assert callable(delegate), 'Invalid delegate %s' % delegate
    assert splitValues is not None, 'A split values regex is required'

    def exploit(value, **data):
        if isinstance(value, str):
            value = splitValues.split(value)
            if normalizeValue is not None:
                for k in range(0, len(value)): value[k] = normalizeValue.sub('', value[k])

        return delegate(value=value, **data)
    return exploit
