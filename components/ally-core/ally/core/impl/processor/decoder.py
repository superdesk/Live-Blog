'''
Created on Aug 23, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the creation for decoders on the request content.
'''

from ally.api.operator.container import Model
from ally.api.operator.type import TypeModelProperty, TypeModel
from ally.api.type import Type, List, Input
from ally.container.ioc import injected
from ally.core.spec.resources import Invoker, Normalizer, Converter
from ally.core.spec.transform.exploit import handleExploitError
from ally.core.spec.transform.support import setterOnObj, obtainOnDict, \
    obtainOnObj
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.exception import InputError, Ref
from ally.internationalization import _
from collections import Callable, deque
from weakref import WeakKeyDictionary
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    invoker = requires(Invoker)
    arguments = requires(dict)
    converterId = requires(Converter)
    converter = requires(Converter)
    normalizer = requires(Normalizer)
    # ---------------------------------------------------------------- Defined
    decoder = defines(Callable, doc='''
    @rtype: Callable
    The decoder to be used for decoding the request content.
    ''')
    decoderData = defines(dict, doc='''
    @rtype: dictionary{string, object}
    The decoder data used in the parsing process.
    ''')

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    isSuccess = defines(bool)
    text = defines(str)

# --------------------------------------------------------------------

@injected
class CreateDecoderHandler(HandlerProcessorProceed):
    '''
    Implementation for a handler that creates the decoders for the request content.
    '''

    def __init__(self):
        super().__init__()

        self._cache = WeakKeyDictionary()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Create the request decoder.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        if response.isSuccess is False: return  # Skip in case the response is in error
        if request.decoder: return  # There is already a decoder no need to create another one
        assert isinstance(request.invoker, Invoker), 'Invalid request invoker %s' % request.invoker

        for inp in request.invoker.inputs:
            assert isinstance(inp, Input)

            if isinstance(inp.type, TypeModel):
                request.decoder = self.decoderFor(inp.name, inp.type)
                if request.decoder is not None:
                    request.decoderData = dict(target=request.arguments, converterId=request.converterId,
                                               converter=request.converter, normalizer=request.normalizer)
                else: assert log.debug('Cannot decode request object \'%s\'', inp.type) or True
                break

    # ----------------------------------------------------------------

    def decoderFor(self, argumentKey, ofType):
        '''
        Create a decoder exploit for the provided type.
        
        @param argumentKey: string
            The argument name to be used for storing the decoded value.
        @param ofType: Type
            The type to create the decoding exploit for.
        @return: callable(**data)
            The exploit that provides the decoding.
        '''
        assert isinstance(argumentKey, str), 'Invalid argument key %s' % argumentKey
        assert isinstance(ofType, Type), 'Invalid type %s' % ofType

        decoder = self._cache.get(ofType)
        if decoder is None:
            assert log.debug('Creating decoder for type \'%s\'', ofType) or True
            if isinstance(ofType, TypeModel):
                assert isinstance(ofType, TypeModel)
                decoder = self.decoderModel(ofType, obtainOnDict(argumentKey, ofType.clazz))
            else:
                assert log.debug('Cannot decode object type \'%s\'', ofType) or True
                return None

            self._cache[ofType] = decoder

        return decoder

    def decoderModel(self, ofType, getter=None, exploit=None):
        '''
        Create a decode exploit for a model.
        
        @param ofType: TypeModel
            The type model to decode.
        @param getter: callable(object) -> object|None
            The getter used to get the model from the target object.
        @param exploit: EncodeObject|None
            The decode model to use.
        @return: callable(**data)
            The exploit that provides the model decoding.
        '''
        assert isinstance(ofType, TypeModel), 'Invalid type model %s' % ofType

        exploit = exploit or DecodeObject(ofType.container.name, getter)
        assert isinstance(exploit, DecodeObject), 'Invalid decode object %s' % exploit

        for typeProp in ofType.propertyTypes():
            assert isinstance(typeProp, TypeModelProperty)

            self.registerProperty(typeProp.property, typeProp, exploit)

        return exploit

    def decoderPrimitive(self, propertyName, typeValue):
        '''
        Create a decode exploit for a primitive property also decodes primitive value list.
        
        @param propertyName: string
            The property name to use for the primitive.
        @param typeValue: Type
            The type of the property value to decode.
        @return: callable(**data)
            The exploit that provides the primitive decoding.
        '''
        assert isinstance(propertyName, str), 'Invalid property name %s' % propertyName
        assert isinstance(typeValue, Type), 'Invalid property value type %s' % typeValue

        if isinstance(typeValue, List):
            assert isinstance(typeValue, List)

            return DecodePrimitiveList(typeValue.itemType, obtainOnObj(propertyName, list))

        return DecodePrimitive(setterOnObj(propertyName), typeValue)

    def decoderId(self, propertyName, typeValue):
        '''
        Create a decode exploit for a property id decode and add it to this model decode.
        
        @param propertyName: string
            The property name to use for the id value.
        @param typeValue: Type
            The type of the property to decode.
        @return: callable(**data)
            The exploit that provides the id decoding.
        '''
        assert isinstance(propertyName, str), 'Invalid property name %s' % propertyName

        return DecodeId(setterOnObj(propertyName), typeValue)

    def decoderProperty(self, propertyName, ofType, exploit=None):
        '''
        Create a decode exploit for a property.
        
        @param propertyName: string
            The property name to use for the property value.
        @param ofType: TypeModelProperty
            The type property to decode.
        @param exploit: EncodeObject|None
            The decode model to use.
        @return: callable(**data)
            The exploit that provides the property decoding.
        '''
        assert isinstance(propertyName, str), 'Invalid property name %s' % propertyName
        assert isinstance(ofType, TypeModelProperty), 'Invalid type model property %s' % ofType
        assert isinstance(ofType.container, Model)

        exploit = exploit or DecodeObject(ofType.container.name)
        assert isinstance(exploit, DecodeObject), 'Invalid decode object %s' % exploit

        self.registerProperty(propertyName, ofType, exploit, False)

        return exploit

    def registerProperty(self, propertyName, typeProp, exploit, withException=True):
        '''
        Register an decode exploit for a property type.
        
        @param propertyName: string
            The property name to use for the property value.
        @param typeProp: TypeProperty
            The property type to create the exploit for.
        @param exploit: EncodeObject
            The encode model to register the property to.
        @param withException: boolean
            Flag indicating that the property should have the validation throw an input error.
        '''
        assert isinstance(propertyName, str), 'Invalid property name %s' % propertyName
        assert isinstance(exploit, DecodeObject), 'Invalid decode model %s' % exploit
        assert isinstance(typeProp, TypeModelProperty), 'Invalid type property %s' % typeProp
        assert isinstance(typeProp.container, Model), 'Invalid model %s' % typeProp.container

        if typeProp.property == typeProp.container.propertyId:
            decoder = self.decoderId(propertyName, typeProp.type)
            expectedType = typeProp.type
        elif isinstance(typeProp.type, TypeModel):
            assert isinstance(typeProp.type, TypeModel)
            decoder = DecodeDelegate(self.decoderId(propertyName, typeProp.type.propertyTypeId().type),
                                     self.decoderProperty(propertyName, typeProp.type.propertyTypeId()))
            expectedType = typeProp.type.propertyTypeId().type
        else:
            decoder = self.decoderPrimitive(propertyName, typeProp.type)
            expectedType = typeProp.type

        def invalidValue(value, **data):
            if isinstance(value, str) and not value.strip(): return True
            raise InputError(Ref(_('Invalid value, expected %(type)s type') % dict(type=_(str(expectedType))),
                                 ref=typeProp))

        if withException: decoder = DecodeFalied(decoder, invalidValue)
        exploit.properties[typeProp.property] = decoder

# --------------------------------------------------------------------

class DecodeFalied:
    '''
    Exploit that wraps an exploit decoding and invokes a interceptor in case the decoding fails by returning a
    different value then True.
    '''
    __slots__ = ('exploit', 'interceptor')

    def __init__(self, exploit, interceptor):
        '''
        Create the error wrapped decoder.
        
        @param exploit: callable
            The wrapped decode exploit.
        @param interceptor: callable
            The interceptor to be invoked if the decoding fails.
        '''
        assert callable(exploit), 'Invalid decode exploit %s' % exploit
        assert callable(interceptor), 'Invalid interceptor %s' % interceptor

        self.exploit = exploit
        self.interceptor = interceptor

    def __call__(self, **data):
        if not self.exploit(**data): return self.interceptor(**data)
        return True

class DecodeObject:
    '''
    Exploit for object decoding.
    '''
    __slots__ = ('name', 'getter', 'properties')

    def __init__(self, name, getter=None):
        '''
        Create a decode exploit for a model.
        
        @param name: string
            The name of the model to decode.
        @param getter: callable(object) -> object
            The getter used to obtain the value object from the target object.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        self.name = name
        self.getter = getter
        self.properties = {}

    def __call__(self, path, target, normalizer, **data):
        assert isinstance(path, deque), 'Invalid path %s' % path
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer

        if not path: return False

        key = path.popleft()
        if not isinstance(key, str): return False
        assert isinstance(key, str), 'Invalid path element %s' % key

        if path and normalizer.normalize(self.name) == key:
            key = path.popleft()
            if not isinstance(key, str): return False

        if self.getter is not None: target = self.getter(target)

        for keyProp, decodeProp in self.properties.items():
            assert isinstance(keyProp, str), 'Invalid property key %s' % keyProp
            if normalizer.normalize(keyProp) == key: break
        else: return False
        try: return decodeProp(path=path, target=target, normalizer=normalizer, **data)
        except InputError: raise
        except: handleExploitError(decodeProp)

class DecodePrimitive:
    '''
    Exploit for primitive decoding.
    '''
    __slots__ = ('setter', 'typeValue')

    def __init__(self, setter, typeValue):
        '''
        Create a decode exploit for a primitive property.
        
        @param setter: callable(object)
            The setter used to set the value to the target object.
        @param typeValue: Type
            The type of the property value to encode.
        '''
        assert callable(setter), 'Invalid setter %s' % setter
        assert isinstance(typeValue, Type), 'Invalid value type %s' % typeValue

        self.setter = setter
        self.typeValue = typeValue

    def __call__(self, path, target, value, converter, **data):
        assert isinstance(path, deque), 'Invalid path %s' % path
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter

        if path: return False
        # Only if there are no other elements in path we process the exploit
        if value is not None:
            if not isinstance(value, str): return False
            # If the value is not a string then is not valid
            try: value = converter.asValue(value, self.typeValue)
            except ValueError: return False
        self.setter(target, value)
        return True

class DecodePrimitiveList(DecodePrimitive):
    '''
    Exploit for primitive decoding with a specified name.
    '''
    __slots__ = ('obtain',)

    def __init__(self, typeItemValue, obtain=None):
        '''
        Create a decode exploit for a primitive property.
        
        @param typeItemValue: Type
            The type of the item value to encode.
        @param obtain: callable(object) -> object|None
            The obtain function to get the list of primitives.
        '''
        assert callable(obtain), 'Invalid obtain %s' % obtain
        super().__init__(list.append, typeItemValue)

        self.obtain = obtain

    def __call__(self, path, target, value, converter, **data):
        if self.obtain is not None: target = self.obtain(target)
        assert isinstance(target, list), 'Invalid target %s' % target

        if isinstance(value, (list, tuple)):
            for item in value:
                if not super().__call__(path, target, item, converter): return False
            return True

        return super().__call__(path, target, value, converter)

class DecodeId(DecodePrimitive):
    '''
    Exploit for id decoding.
    '''
    __slots__ = ()

    def __call__(self, path, target, value, converterId, **data):
        return super().__call__(path, target, value, converterId)

class DecodeDelegate:
    '''
    Exploit for delegating to other decoders, it will stop when the first delegate has returned True.
    '''
    __slots__ = ('delegates',)

    def __init__(self, *delegates):
        '''
        Create the decoder delegate.
        
        @param delegates: arguments[callable(**data)]
            The delegates exploits to delegate to.
        '''
        for delegate in delegates: assert callable(delegate), 'Invalid delegate %s' % delegate

        self.delegates = delegates

    def __call__(self, **data):
        for delegate in self.delegates:
            if delegate(**data): return True
        return False
