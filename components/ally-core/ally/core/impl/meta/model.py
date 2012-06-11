'''
Created on May 30, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the models meta encoders and decoders.
'''

from ally.api.operator.container import Model
from ally.api.operator.type import TypeModel, TypeModelProperty, TypeProperty
from ally.api.type import Type, Iter, TypeNone, Boolean, Integer, Number, \
    Percentage, String, Time, Date, DateTime, typeFor
from ally.container.ioc import injected
from ally.core.impl.meta.decode import DecodeObject, DecodeValue, \
    DecodeGetterIdentifier, DecodeList, DecodeGetter
from ally.core.impl.meta.encode import EncodeCollection, EncodeObject, \
    EncodeValue, EncodeGetterIdentifier, EncodeIdentifier
from ally.core.impl.meta.general import obtainOnDict, setterOnObj, \
    getterOnObjIfIn, obtainOnObj
from ally.core.spec.context import TransformModel, ConstructMetaModel
from ally.core.spec.meta import IMetaService, SAMPLE, Value
from ally.core.spec.resources import Converter
from collections import deque
from weakref import WeakKeyDictionary
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ModelMetaService(IMetaService):
    '''
    @see: IMetaService impementation for handling the models meta.
    This service will provide a decode that will be able to work with identifiers:
        string, list[string], tuple(string), deque[string]
        
    and encode meta will only have string identifiers.
    '''

    nameList = '%sList'
    # The name to use for rendering lists of models.
    nameValue = 'Value'
    # The name to use for rendering the values in a list of values.
    typeOrders = [Boolean, Integer, Number, Percentage, String, Time, Date, DateTime, Iter]
    # The order in which 

    def __init__(self):
        assert isinstance(self.nameList, str), 'Invalid name list %s' % self.nameList
        assert isinstance(self.nameValue, str), 'Invalid name value %s' % self.nameValue
        assert isinstance(self.typeOrders, list), 'Invalid type orders %s' % self.typeOrders

        self._typeOrders = [typeFor(typ) for typ in self.typeOrders]

        self._cacheDecode = WeakKeyDictionary()
        self._cacheEncode = WeakKeyDictionary()

    def createDecode(self, context):
        '''
        @see: IMetaService.createDecode
        '''
        assert isinstance(context, ConstructMetaModel), 'Invalid context %s' % context
        assert isinstance(context.modelType, TypeModel), 'Invalid model type %s' % context.modelType
        clazz, model = context.modelType.clazz, context.modelType.container
        assert isinstance(model, Model)

        decoder = self._cacheDecode.get(context.modelType, None)
        if decoder is not None: return decoder

        decoder = DecodeObject()
        for prop, propType in model.properties.items():
            setter = setterOnObj(prop)
            if prop == model.propertyId:
                dprop = DecodeId(setter, propType)
            elif isinstance(propType, TypeModel):
                dprop = DecodeId(setter, propType.container.properties[propType.container.propertyId])
            elif isinstance(propType, Iter):
                assert isinstance(propType, Iter)
                dprop = DecodeList(DecodeValue(list.append, propType.itemType))
                dprop = DecodeGetter(dprop, obtainOnObj(prop, list))
            else:
                dprop = DecodeValue(setter, propType)
            decoder.properties[prop] = dprop

        decoder = DecodeGetterIdentifier(decoder, obtainOnDict(context.modelType, clazz), model.name)

        self._cacheDecode[context.modelType] = decoder
        return decoder

    # --------------------------------------------------------------------

    def createEncode(self, context):
        '''
        @see: IMetaService.createEncode
        '''
        assert isinstance(context, ConstructMetaModel), 'Invalid context %s' % context
        typ = context.modelType
        assert isinstance(typ, Type), 'Invalid context type %s' % typ

        encoder = self._cacheEncode.get(typ)
        if encoder is not None: return encoder

        if isinstance(typ, Iter):
            assert isinstance(typ, Iter)
            if isinstance(typ.itemType, (TypeModel, TypeModelProperty)):
                context.modelType = typ.itemType
                encoder = EncodeCollection(self.createEncode(context))
                assert isinstance(typ.itemType.container, Model)
                identifier = self.nameList % typ.itemType.container.name
                encoder = EncodeIdentifier(encoder, identifier)

        elif isinstance(typ, TypeNone):
            assert log.debug('Nothing to encode') or True
            encoder = EncodeObject()

        elif isinstance(typ, TypeModel):
            assert isinstance(typ, TypeModel)

            encoder = EncodeObject()
            types = list(typ.childTypes())
            types.remove(typ.childTypeId())
            types.sort(key=lambda propType: propType.property)
            types.sort(key=self.sortTypeProperties)
            types.insert(0, typ.childTypeId())

            for propType in types: encoder.properties.append(self.encodeProperty(propType))
            encoder = EncodeIdentifier(encoder, typ.container.name)

        elif isinstance(typ, TypeModelProperty):
            assert isinstance(typ, TypeModelProperty)

            encoder = EncodeObject()
            encoder.properties.append(self.encodeProperty(typ))
            encoder = EncodeIdentifier(encoder, typ.container.name)

        else:
            assert log.debug('Cannot encode object type %r', typ) or True
            return None

        self._cacheEncode[typ] = encoder
        return encoder

    def sortTypeProperties(self, propType):
        '''
        Provides the sorting for property types.
        '''
        assert isinstance(propType, TypeProperty), 'Invalid property type %s' % propType
        for k, ord in enumerate(self._typeOrders):
            if propType.type == ord: break
        return k

    def encodeProperty(self, propType):
        '''
        Create an encode for the provided property type.
        
        @param propType: TypeModelProperty
            The property type to create the encode for.
        '''
        assert isinstance(propType, TypeModelProperty), 'Invalid property type %s' % propType
        assert isinstance(propType.container, Model)
        ptype = propType.type

        if propType.property == propType.container.propertyId:
            eprop = EncodeId(ptype)
        elif isinstance(ptype, Iter):
            assert isinstance(ptype, Iter)
            eprop = EncodeCollection(EncodeIdentifier(EncodeValue(ptype.itemType), self.nameValue))
        elif isinstance(ptype, TypeModel):
            assert isinstance(ptype.container, Model)
            eprop = EncodeValue(ptype.container.properties[ptype.container.propertyId])
        else:
            eprop = EncodeValue(propType.type)

        return EncodeGetterIdentifier(eprop, getterOnObjIfIn(propType.property, propType), propType.property)

# --------------------------------------------------------------------

class DecodeId(DecodeValue):
    '''
    Extension for @see: DecodeValue that uses a different converter that is special for Id.
    '''

    def decode(self, identifier, value, obj, context):
        '''
        IMetaDecode.decode
        '''
        assert isinstance(context, TransformModel), 'Invalid context %s' % context
        assert isinstance(context.converterId, Converter)

        if not isinstance(identifier, deque): return False
        if identifier: return False
        # If there are more elements in the paths it means that this decoder should not process the value

        if not isinstance(value, str): return False
        # If the value is not a string then is not valid
        try: value = context.converterId.asValue(value, self.type)
        except ValueError: return False

        self.setter(obj, value)
        return True

# --------------------------------------------------------------------

class EncodeId(EncodeValue):
    '''
    Extension for @see: EncodeValue that uses a different converter that is special for Id.
    '''

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        assert isinstance(context, TransformModel), 'Invalid context %s' % context
        assert isinstance(context.converterId, Converter)

        if obj is SAMPLE: value = 'a %s id value' % self.type
        else: value = context.converterId.asString(obj, self.type)
        return Value(value=value)
