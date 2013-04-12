'''
Created on Jun 22, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the creation for encoder on the response.
'''

from ally.api.operator.container import Container, Model
from ally.api.operator.type import TypeExtension, TypeProperty, \
    TypeModelProperty, TypeModel
from ally.api.type import Type, Iter, Boolean, Integer, Number, Percentage, \
    String, Time, Date, DateTime, TypeNone, typeFor
from ally.container.ioc import injected
from ally.core.spec.resources import Invoker, Normalizer, Converter
from ally.core.spec.transform.exploit import IResolve, handleExploitError
from ally.core.spec.transform.render import IRender
from ally.core.spec.transform.support import getterOnObjIfIn
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from collections import Callable, Iterable, OrderedDict
from weakref import WeakKeyDictionary
import logging
from ally.exception import DevelError

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    invoker = requires(Invoker)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    converterId = requires(Converter)
    converter = requires(Converter)
    normalizer = requires(Normalizer)
    isSuccess = requires(bool)
    # ---------------------------------------------------------------- Defined
    encoder = defines(Callable, doc='''
    @rtype: Callable
    The encoder to be used for encoding the response object for content rendering.
    ''')
    encoderData = defines(dict, doc='''
    @rtype: dictionary{string, object}
    The encoder data used in the rendering process.
    ''')

# --------------------------------------------------------------------

@injected
class CreateEncoderHandler(HandlerProcessorProceed):
    '''
    Implementation for a handler that provides the creation of encoders for response objects.
    '''

    nameList = '%sList'
    # The name to use for rendering lists of models.
    nameValue = 'Value'
    # The name to use for rendering the values in a list of values.
    typeOrders = [Boolean, Integer, Number, Percentage, String, Time, Date, DateTime, Iter]
    # The order in which 

    def __init__(self):
        '''
        Construct the encoder.
        '''
        assert isinstance(self.nameList, str), 'Invalid name list %s' % self.nameList
        assert isinstance(self.nameValue, str), 'Invalid name value %s' % self.nameValue
        assert isinstance(self.typeOrders, list), 'Invalid type orders %s' % self.typeOrders
        super().__init__()

        self._typeOrders = [typeFor(typ) for typ in self.typeOrders]
        self._cache = WeakKeyDictionary()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Create the response content encoder.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        if response.isSuccess is False: return  # Skip in case the response is in error
        if response.encoder: return  # There is already an encoder no need to create another one
        assert isinstance(request.invoker, Invoker), 'Invalid request invoker %s' % request.invoker

        response.encoder = self.encoderFor(request.invoker.output)
        if response.encoder is None: raise DevelError('Cannot encode response object \'%s\'' % request.invoker.output)

        response.encoderData = dict(converterId=response.converterId, converter=response.converter,
                                    normalizer=response.normalizer)

    # ----------------------------------------------------------------

    def encoderFor(self, ofType):
        '''
        Create a encode exploit for the provided type.
        
        @param ofType: Type
            The type to create the encoding exploit for.
        @return: callable(**data)
            The exploit that provides the encoding.
        '''
        assert isinstance(ofType, Type), 'Invalid type %s' % ofType

        encoder = self._cache.get(ofType)
        if encoder is None:
            assert log.debug('Creating encoder for type \'%s\'', ofType) or True
            if isinstance(ofType, Iter):
                assert isinstance(ofType, Iter)

                nameEncoder = self.encoderItem(ofType.itemType)
                if nameEncoder is not None:
                    name, encoderItem = nameEncoder
                    encoder = EncodeCollection(name, encoderItem)

            elif isinstance(ofType, TypeModel):
                encoder = self.encoderModel(ofType)

            elif isinstance(ofType, TypeModelProperty):
                assert isinstance(ofType, TypeModelProperty)

                encoder = self.encoderProperty(ofType)

            elif isinstance(ofType, TypeNone) or ofType.isOf(bool):
                encoder = lambda **data: None

            else: assert log.debug('Cannot encode object type \'%s\'', ofType) or True
            self._cache[ofType] = encoder

        return encoder

    def encoderItem(self, ofType):
        '''
        Creates the item encoder for the collection.
        
        @param ofType: Type
            The type of the item.
        @return: tuple(string, callable(**data))|None
            The name of the collection and exploit that provides the item encoding, None if the item type could not be
            solved.
        '''
        assert isinstance(ofType, Type), 'Invalid type %s' % ofType

        if isinstance(ofType, (TypeModel, TypeModelProperty)):
            assert isinstance(ofType.container, Model), 'Invalid model %s' % ofType.container

            return self.nameList % ofType.container.name, self.encoderFor(ofType)
        else:
            log.debug('Cannot encode collection item type \'%s\'', ofType.itemType) or True

    def encoderModel(self, ofType, getter=None, exploit=None):
        '''
        Create a encode exploit for a model.
        
        @param ofType: TypeModel
            The type model to encode.
        @param getter: callable(object) -> object|None
            The getter used to get the model from the value object.
        @param exploit: EncodeObject|None
            The encode model to use.
        @return: callable(**data)
            The exploit that provides the model encoding.
        '''
        assert isinstance(ofType, TypeModel), 'Invalid type model %s' % ofType

        typesProps = list(ofType.propertyTypes())
        if ofType.hasId(): typesProps.remove(ofType.propertyTypeId())
        typesProps.sort(key=lambda typeProp: typeProp.property)
        typesProps.sort(key=self.sortTypePropertyKey)
        if ofType.hasId(): typesProps.insert(0, ofType.propertyTypeId())

        exploit = exploit or EncodeObject(ofType.container.name, getter)
        assert isinstance(exploit, EncodeObject), 'Invalid encode object %s' % exploit

        for typeProp in typesProps:
            assert isinstance(typeProp, TypeModelProperty)

            self.registerProperty(exploit, typeProp, getterOnObjIfIn(typeProp.property, typeProp))

        return exploit

    def encoderPrimitive(self, typeValue, getter=None):
        '''
        Create a encode exploit for a primitive property also encodes primitive value list.
        
        @param typeValue: Type
            The type of the property value to encode.
        @param getter: callable(object) -> object|None
            The getter used to get the value from the value object, if None provided it will use the received value.
        @return: callable(**data)
            The exploit that provides the primitive encoding.
        '''
        assert isinstance(typeValue, Type), 'Invalid property value type %s' % typeValue
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        if isinstance(typeValue, Iter):
            assert isinstance(typeValue, Iter)

            return EncodePrimitiveCollection(self.nameValue, typeValue.itemType, getter)

        return EncodePrimitive(typeValue, getter)

    def encoderId(self, typeValue, getter=None):
        '''
        Create a encode exploit for a property id encode and add it to this model encode.
        
        @param typeValue: Type
            The type of the property to encode.
        @param getter: callable(object) -> object|None
            The getter used to get the value from the model object, if None provided it will use the received value.
        @return: callable(**data)
            The exploit that provides the id encoding.
        '''
        assert isinstance(typeValue, Type), 'Invalid property type %s' % typeValue
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        return EncodeId(typeValue, getter)

    def encoderProperty(self, ofType, getter=None, exploit=None):
        '''
        Create a encode exploit for a property.
        
        @param ofType: TypeModelProperty
            The type property to encode.
        @param getter: callable(object) -> object|None
            The getter used to get the property from the value object.
        @param exploit: EncodeObject|None
            The encode model to use.
        @return: callable(**data)
            The exploit that provides the property encoding.
        '''
        assert isinstance(ofType, TypeModelProperty), 'Invalid type model property %s' % ofType
        assert isinstance(ofType.container, Model)

        exploit = exploit or EncodeObject(ofType.container.name, getter)
        assert isinstance(exploit, EncodeObject), 'Invalid encode object %s' % exploit

        self.registerProperty(exploit, ofType)

        return exploit

    def registerProperty(self, exploit, typeProp, getter=None):
        '''
        Register an encode exploit for a property type.
        
        @param exploit: EncodeObject
            The encode model to register the property to.
        @param typeProp: TypeProperty
            The property type to create the exploit for.
        @param getter: callable(object) -> object|None
            The getter used to get the value from the value object, if None provided it will use the received value.
        '''
        assert isinstance(exploit, EncodeObject), 'Invalid encode model %s' % exploit
        assert isinstance(typeProp, TypeProperty), 'Invalid type property %s' % typeProp

        if typeProp.property == typeProp.container.propertyId:
            encoder = self.encoderId(typeProp.type, getter)
        elif isinstance(typeProp.type, TypeModel):
            assert isinstance(typeProp.type, TypeModel)
            encoder = self.encoderProperty(typeProp.type.propertyTypeId(), getter)
        else:
            encoder = self.encoderPrimitive(typeProp.type, getter)
        exploit.properties[typeProp.property] = encoder

    def sortTypePropertyKey(self, propType):
        '''
        Provides the sorting key for property types, used in sort functions.
        '''
        assert isinstance(propType, TypeProperty), 'Invalid property type %s' % propType

        for k, ord in enumerate(self._typeOrders):
            if propType.type == ord: break
        return k

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
        for nameProp, encodeProp in self.properties.items():
            try: encodeProp(name=nameProp, **data)
            except: handleExploitError(encodeProp)
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

    def __call__(self, value, normalizer, converter, render, resolve, name=None, **data):
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(resolve, IResolve), 'Invalid resolve %s' % resolve

        if self.getter: value = self.getter(value)
        if value is None: return
        assert isinstance(value, Iterable), 'Invalid value %s' % value

        typeValue = typeFor(value)
        if typeValue and isinstance(typeValue, TypeExtension):
            assert isinstance(typeValue, TypeExtension)
            assert isinstance(typeValue.container, Container)
            attrs = {}
            for prop, propType in typeValue.container.properties.items():
                propValue = getattr(value, prop)
                if propValue is not None: attrs[normalizer.normalize(prop)] = converter.asString(propValue, propType)
        else: attrs = None

        data.update(normalizer=normalizer, converter=converter, render=render, resolve=resolve)

        render.collectionStart(normalizer.normalize(name or self.name), attrs)
        resolve.queueBatch(self.exploitItem, (dict(data, value=item) for item in value))
        resolve.queue(self.finalize, render=render)

    def finalize(self, render, **data):
        assert isinstance(render, IRender), 'Invalid render %s' % render

        render.collectionEnd()

class EncodePrimitive:
    '''
    Exploit for primitive encoding.
    '''
    __slots__ = ('typeValue', 'getter')

    def __init__(self, typeValue, getter=None):
        '''
        Create a encode exploit for a primitive property.
        
        @param typeValue: Type
            The type of the property value to encode.
        @param getter: callable(object) -> object|None
            The getter used to get the value from the value object, if None provided it will use the received value.
        '''
        assert isinstance(typeValue, Type), 'Invalid value type %s' % typeValue
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        self.typeValue = typeValue
        self.getter = getter

    def __call__(self, name, value, render, normalizer, converter, **data):
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter

        if self.getter: value = self.getter(value)
        if value is None: return
        assert self.typeValue.isValid(value), 'Invalid value \'%s\' for type %s' % (value, self.typeValue) 
        render.value(normalizer.normalize(name), converter.asString(value, self.typeValue))

class EncodePrimitiveCollection(EncodePrimitive):
    '''
    Exploit for primitive encoding with a specified name.
    '''
    __slots__ = ('nameValue', 'getterCollection')

    def __init__(self, nameValue, typeValue, getter=None):
        '''
        Create a encode exploit for a primitive property.
        @see: EncodePrimitive.__init__
        
        @param nameValue: string
            The name to associate with the rendered value.
        '''
        assert isinstance(nameValue, str), 'Invalid value name %s' % nameValue
        assert getter is None or callable(getter), 'Invalid getter %s' % getter
        super().__init__(typeValue)

        self.nameValue = nameValue
        self.getterCollection = getter

    def __call__(self, name, value, render, normalizer, converter, **data):
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter

        if self.getterCollection: value = self.getterCollection(value)
        if value is None: return
        assert isinstance(value, Iterable), 'Invalid value %s' % value

        render.collectionStart(name)
        for item in value:
            super().__call__(self.nameValue, item, render, normalizer, converter)
        render.collectionEnd()

class EncodeId(EncodePrimitive):
    '''
    Exploit for id encoding.
    '''
    __slots__ = ()

    def __call__(self, name, value, render, converterId, **data):
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(converterId, Converter), 'Invalid converter id %s' % converterId

        if self.getter: value = self.getter(value)
        if value is None: return
        render.value(name, converterId.asString(value, self.typeValue))
