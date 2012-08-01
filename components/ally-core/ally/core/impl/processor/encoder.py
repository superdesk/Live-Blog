'''
Created on Jun 22, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation for encoding the response.
'''

from ally.api.operator.container import Model
from ally.api.operator.type import TypeProperty, TypeModelProperty, TypeModel
from ally.api.type import Type, Iter, Boolean, Integer, Number, Percentage, \
    String, Time, Date, DateTime, typeFor, TypeNone
from ally.container.ioc import injected
from ally.core.spec.codes import Code, BAD_CONTENT
from ally.core.spec.encdec.encode import EncodeCollection, EncodeObject
from ally.core.spec.encdec.render import IRender
from ally.core.spec.encdec.support import getterOnObjIfIn
from ally.core.spec.resources import Converter, Normalizer, Invoker
from ally.design.context import defines, Context, requires
from ally.design.processor import HandlerProcessorProceed
from collections import Callable, Iterable
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

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    converterId = requires(Converter)
    converter = requires(Converter)
    normalizer = requires(Normalizer)
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
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
    Implementation for a handler that provides the transformation of model object types into encoders.
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

        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error
        assert isinstance(request.invoker, Invoker), 'Invalid request invoker %s' % request.invoker

        response.encoder = self.encoderFor(request.invoker.output)
        if response.encoder is None:
            response.code, response.text = BAD_CONTENT, 'Cannot encode response object'
            return

        response.encoderData = dict(converterId=response.converterId, converter=response.converter,
                                    normalizer=response.normalizer)

    # ----------------------------------------------------------------

    def encoderFor(self, ofType):
        '''
        Create a encode exploit for the provided type.
        
        @param ofType: Type
            The type to create the encoding exploit for.
        @param getter: callable(object) -> object|None
            The getter used to get the value.
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
                    encoder = EncodeCollection(self.nameList % name, encoderItem)

            elif isinstance(ofType, TypeNone):
                encoder = lambda **data: None

            elif isinstance(ofType, TypeModel):
                encoder = self.encoderModel(ofType)

            elif isinstance(ofType, TypeModelProperty):
                assert isinstance(ofType, TypeModelProperty)

                encoder = self.encoderProperty(ofType)

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

            return ofType.container.name, self.encoderFor(ofType)
        else:
            log.debug('Cannot encode collection item type \'%s\'', ofType.itemType) or True

    def encoderPrimitive(self, typeValue, getterProp=None):
        '''
        Create a encode exploit for a primitive property also encodes primitive value list.
        
        @param typeValue: Type
            The type of the property value to encode.
        @param getterProp: callable(object) -> object|None
            The getter used to get the value from the value object, if None provided it will use the received value.
        @return: callable(**data)
            The exploit that provides the primitive encoding.
        '''
        assert isinstance(typeValue, Type), 'Invalid property value type %s' % typeValue
        assert getterProp is None or callable(getterProp), 'Invalid getter %s' % getterProp

        def exploit(name, value, render, normalizer, converter, **data):
            assert isinstance(name, str), 'Invalid name %s' % name
            assert isinstance(render, IRender), 'Invalid render %s' % render
            assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
            assert isinstance(converter, Converter), 'Invalid converter %s' % converter

            if getterProp: value = getterProp(value)
            if value is None: return
            if isinstance(typeValue, Iter):
                assert isinstance(value, Iterable), 'Invalid value %s' % value

                render.collectionStart(name)
                nameValue = normalizer.normalize(self.nameValue)
                for item in value:
                    render.value(nameValue, converter.asString(item, typeValue.itemType))
                render.collectionEnd()
            else:
                render.value(name, converter.asString(value, typeValue))

        return exploit

    def encoderId(self, typeValue, getterProp=None):
        '''
        Create a encode exploit for a property id encode and add it to this model encode.
        
        @param typeValue: Type
            The type of the property to encode.
        @param getterProp: callable(object) -> object|None
            The getter used to get the value from the model object, if None provided it will use the received value.
        @return: callable(**data)
            The exploit that provides the id encoding.
        '''
        assert isinstance(typeValue, Type), 'Invalid property type %s' % typeValue
        assert getterProp is None or callable(getterProp), 'Invalid getter %s' % getterProp

        def exploit(name, value, render, converterId, **data):
            assert isinstance(name, str), 'Invalid name %s' % name
            assert isinstance(render, IRender), 'Invalid render %s' % render
            assert isinstance(converterId, Converter), 'Invalid converter id %s' % converterId

            if getterProp: value = getterProp(value)
            if value is None: return
            render.value(name, converterId.asString(value, typeValue))

        return exploit

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
        assert getter is None or callable(getter), 'Invalid getter %s' % getter
        assert isinstance(ofType.container, Model)

        exploit = exploit or EncodeObject(ofType.container.name, getter)
        assert isinstance(exploit, EncodeObject), 'Invalid encode object %s' % exploit

        self.registerProperty(exploit, ofType)

        return exploit

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
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        typesProps = list(ofType.childTypes())
        typesProps.remove(ofType.childTypeId())
        typesProps.sort(key=lambda typeProp: typeProp.property)
        typesProps.sort(key=self.sortTypePropertyKey)
        typesProps.insert(0, ofType.childTypeId())

        exploit = exploit or EncodeObject(ofType.container.name, getter)
        assert isinstance(exploit, EncodeObject), 'Invalid encode object %s' % exploit

        for typeProp in typesProps:
            assert isinstance(typeProp, TypeModelProperty)

            self.registerProperty(exploit, typeProp, getterOnObjIfIn(typeProp.property, typeProp))

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
            exploit.properties[typeProp.property] = self.encoderId(typeProp.type, getter)
        elif isinstance(typeProp.type, TypeModel):
            assert isinstance(typeProp.type, TypeModel)
            exploit.properties[typeProp.property] = self.encoderProperty(typeProp.type.childTypeId(), getter)
        else:
            exploit.properties[typeProp.property] = self.encoderPrimitive(typeProp.type, getter)

    def sortTypePropertyKey(self, propType):
        '''
        Provides the sorting key for property types, used in sort functions.
        '''
        assert isinstance(propType, TypeProperty), 'Invalid property type %s' % propType

        for k, ord in enumerate(self._typeOrders):
            if propType.type == ord: break
        return k
