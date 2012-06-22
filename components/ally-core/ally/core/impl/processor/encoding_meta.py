'''
Created on Jun 22, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation for encoding the response.
'''

from ally.api.operator.container import Model
from ally.api.operator.type import TypeModel, TypeModelProperty, TypeProperty
from ally.api.type import Type, Iter, TypeNone, Boolean, Integer, Number, \
    Percentage, String, Time, Date, DateTime, typeFor
from ally.container.ioc import injected
from ally.core.impl.meta.encode import EncodeCollection, EncodeObject, \
    EncodeValue, EncodeGetterIdentifier, EncodeIdentifier
from ally.core.impl.meta.general import getterOnObjIfIn, Conversion
from ally.core.spec.codes import Code, BAD_CONTENT
from ally.core.spec.meta import Meta, SAMPLE, Value, IMetaEncode
from ally.core.spec.resources import Converter
from ally.design.context import defines, Context, requires
from ally.design.processor import HandlerProcessorProceed
from weakref import WeakKeyDictionary
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    metaForType = requires(Type)
    obj = requires(object)
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)

class ResponseContent(Conversion):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Required
    converterId = requires(Converter)
    # ---------------------------------------------------------------- Defined
    meta = defines(Meta, doc='''
    @rtype: Meta
    The meta object used in rendering the response.
    ''')

# --------------------------------------------------------------------

@injected
class EncodingMetaHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments.
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
        super().__init__()

        self._typeOrders = [typeFor(typ) for typ in self.typeOrders]
        self._cacheEncode = WeakKeyDictionary()

    def process(self, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Create the meta responsable for encoding the response.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error

        assert isinstance(response.metaForType, Type), 'Invalid response meta for type %s' % response.metaForType

        encoder = self._cacheEncode.get(response.metaForType)
        if encoder is not None: return encoder

        encoder = self.encodeType(response.metaForType)
        if encoder is None:
            response.code, response.text = BAD_CONTENT, 'Cannot encode response object'
            return
        assert isinstance(encoder, IMetaEncode), 'Invalid meta encoder %s' % encoder

        self._cacheEncode[response.metaForType] = encoder

        responseCnt.meta = encoder.encode(response.obj, responseCnt)

    # --------------------------------------------------------------------

    def encodeType(self, typ):
        '''
        Create an encode for the provided type.
        
        @param typ: Type
            The type to create the encode for.
        '''
        assert isinstance(typ, Type), 'Invalid context type %s' % typ

        if isinstance(typ, Iter):
            assert isinstance(typ, Iter)
            if isinstance(typ.itemType, (TypeModel, TypeModelProperty)):
                encoder = EncodeCollection(self.encodeType(typ.itemType))
                assert isinstance(typ.itemType.container, Model)
                identifier = self.nameList % typ.itemType.container.name
                return EncodeIdentifier(encoder, identifier)

        elif isinstance(typ, TypeNone):
            assert log.debug('Nothing to encode') or True
            return EncodeObject()

        elif isinstance(typ, TypeModel):
            assert isinstance(typ, TypeModel)

            encoder = EncodeObject()
            types = list(typ.childTypes())
            types.remove(typ.childTypeId())
            types.sort(key=lambda propType: propType.property)
            types.sort(key=self.sortTypeProperties)
            types.insert(0, typ.childTypeId())

            for propType in types: encoder.properties.append(self.encodeProperty(propType))
            return EncodeIdentifier(encoder, typ.container.name)

        elif isinstance(typ, TypeModelProperty):
            assert isinstance(typ, TypeModelProperty)

            encoder = EncodeObject()
            encoder.properties.append(self.encodeProperty(typ))
            return EncodeIdentifier(encoder, typ.container.name)

        else: assert log.debug('Cannot encode object type %r', typ) or True

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

    def sortTypeProperties(self, propType):
        '''
        Provides the sorting for property types.
        '''
        assert isinstance(propType, TypeProperty), 'Invalid property type %s' % propType
        for k, ord in enumerate(self._typeOrders):
            if propType.type == ord: break
        return k

class EncodeId(EncodeValue):
    '''
    Extension for @see: EncodeValue that uses a different converter that is special for Id.
    '''

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        assert isinstance(context, ResponseContent), 'Invalid context %s' % context
        assert isinstance(context.converterId, Converter)

        if obj is SAMPLE: value = 'a %s id value' % self.type
        else: value = context.converterId.asString(obj, self.type)
        return Value(value=value)


