'''
Created on Jul 6, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the models encoding.
'''

from ally.api.operator.container import Model
from ally.api.operator.type import TypeModel, TypeProperty, TypeModelProperty
from ally.api.type import Type, Iter, Boolean, Integer, Number, Percentage, \
    String, Time, Date, DateTime, typeFor, TypeNone
from ally.container.ioc import injected
from ally.core.spec.encdec.exploit import IResolve
from ally.core.spec.encdec.render import IRender
from ally.core.spec.encdec.support import getterOnObjIfIn
from ally.core.spec.resources import Converter, Normalizer
from collections import Iterable, OrderedDict
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ModelEncoder:
    '''
    Implementation that provides the model transformation.
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

    def encodeNone(self):
        '''
        Create a encode exploit for encoding none.
        
        @return: callable(**data)
            The exploit that provides the none encoding.
        '''
        def exploit(**data): pass
        return exploit

    def encodeProperty(self, typeProp, getterProp=None):
        '''
        Create a encode exploit for a property.
        
        @param typeProp: TypeModelProperty
            The type property to encode.
        @param getterProp: callable(object) -> object|None
            The getter used to get the property from the value object.
        @return: callable(**data)
            The exploit that provides the property encoding.
        '''
        assert isinstance(typeProp, TypeModelProperty), 'Invalid type model property %s' % typeProp
        assert getterProp is None or callable(getterProp), 'Invalid getter %s' % getterProp
        assert isinstance(typeProp.parent, TypeModel)

        exploit = EncodeModel(self, typeProp.parent.container.name)
        exploit.encodeProperty(typeProp, getterProp)

        return exploit

    def encodeModel(self, typeModel, getterModel=None):
        '''
        Create a encode exploit for a model.
        
        @param typeModel: TypeModel
            The type model to encode.
        @param getterModel: callable(object) -> object|None
            The getter used to get the model from the value object.
        @return: callable(**data)
            The exploit that provides the model encoding.
        '''
        assert isinstance(typeModel, TypeModel), 'Invalid type model %s' % typeModel
        assert getterModel is None or callable(getterModel), 'Invalid getter %s' % getterModel

        typesProps = list(typeModel.childTypes())
        typesProps.remove(typeModel.childTypeId())
        typesProps.sort(key=lambda typeProp: typeProp.property)
        typesProps.sort(key=self.sortTypeProperties)
        typesProps.insert(0, typeModel.childTypeId())

        exploit = EncodeModel(self, typeModel.container.name, getterModel)
        for typeProp in typesProps:
            assert isinstance(typeProp, TypeModelProperty)
            exploit.encodeProperty(typeProp, getterOnObjIfIn(typeProp.property, typeProp))

        return exploit

    def encodeCollection(self, name, exploitItem, getterCollection=None):
        '''
        Create a encode exploit for a collection.
        
        @param name: string
            The name to use for the collection.
        @param exploitItem: callable(**data)
            The exploit to be used for the item encoding.
        @param getterCollection: callable(object) -> object|None
            The getter used to get the model collection from the value object.
        @return: callable(**data)
            The exploit that provides the model collection encoding.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert callable(exploitItem), 'Invalid exploit %s' % exploitItem
        assert getterCollection is None or callable(getterCollection), 'Invalid getter %s' % getterCollection

        def exploit(value, normalizer, render, resolve, **data):
            assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
            assert isinstance(render, IRender), 'Invalid render %s' % render
            assert isinstance(resolve, IResolve), 'Invalid resolve %s' % resolve

            if getterCollection is not None: value = getterCollection(value)
            if value is None: return
            assert isinstance(value, Iterable), 'Invalid value %s' % value

            data.update(normalizer=normalizer, render=render, resolve=resolve)
            assert log.debug('Started the rendering for collection \'%s\'' % name) or True
            render.collectionStart(normalizer.normalize(name))
            resolve.queueBatch(exploitItem, (dict(data, value=item) for item in value))
            def finalize(**data):
                assert log.debug('Finalized the rendering for collection \'%s\'' % name) or True
                render.collectionEnd()
            resolve.queue(finalize)

        return exploit

    def encode(self, typeOf):
        '''
        Create a encode exploit for the provided type.
        
        @param typeOf: Type
            The type to create the encoding exploit for.
        @return: callable(**data)
            The exploit that provides the encoding.
        '''
        assert isinstance(typeOf, Type), 'Invalid type %s' % typeOf

        if isinstance(typeOf, Iter):
            assert isinstance(typeOf, Iter)
            if isinstance(typeOf.itemType, (TypeModel, TypeModelProperty)):
                exploitItem = self.encode(typeOf.itemType)
                if exploitItem is not None:
                    return self.encodeCollection(self.nameList % typeOf.itemType.container.name, exploitItem)
            else:
                log.debug('Cannot encode collection item type \'%s\'', typeOf.itemType) or True

        elif isinstance(typeOf, TypeNone):
            return self.encodeNone()

        elif isinstance(typeOf, TypeModel):
            return self.encodeModel(typeOf)

        elif isinstance(typeOf, TypeModelProperty):
            assert isinstance(typeOf, TypeModelProperty)

            return self.encodeProperty(typeOf)

        else: log.debug('Cannot encode object type \'%s\'', typeOf) or True

    # ----------------------------------------------------------------

    def sortTypeProperties(self, propType):
        '''
        Provides the sorting for property types.
        '''
        assert isinstance(propType, TypeProperty), 'Invalid property type %s' % propType
        for k, ord in enumerate(self._typeOrders):
            if propType.type == ord: break
        return k

# --------------------------------------------------------------------

class EncodeModel:
    '''
    Exploit for model encoding.
    '''
    __slots__ = ('encoder', 'name', 'getterModel', 'properties')

    def __init__(self, encoder, name, getterModel=None):
        '''
        Create a encode exploit for a model.
        
        @param encoder: ModelEncoder
            The encoder that created the model encode.
        @param name: string
            The name of the model to encode.
        @param getterModel: callable(object) -> object|None
            The getter used to get the model from the value object.
        '''
        assert isinstance(encoder, ModelEncoder), 'Invalid encoder %s' % encoder
        assert isinstance(name, str), 'Invalid name %s' % name
        assert getterModel is None or callable(getterModel), 'Invalid getter %s' % getterModel

        self.encoder = encoder
        self.name = name
        self.getterModel = getterModel
        self.properties = OrderedDict()

    def encodeId(self, typeValue, getterProp=None):
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

            if getterProp is not None: value = getterProp(value)
            if value is None: return
            render.value(name, converterId.asString(value, typeValue))

        return exploit

    def encodePrimitive(self, typeValue, getterProp=None):
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

            if getterProp is not None: value = getterProp(value)
            if value is None: return
            if isinstance(typeValue, Iter):
                assert isinstance(value, Iterable), 'Invalid value %s' % value

                render.collectionStart(name)
                nameValue = normalizer.normalize(self.encoder.nameValue)
                for item in value:
                    render.value(nameValue, converter.asString(item, typeValue.itemType))
                render.collectionEnd()
            else:
                render.value(name, converter.asString(value, typeValue))

        return exploit

    def encodeProperty(self, typeProp, getterProp=None):
        '''
        Create a encode exploit for a property type.
        
        @param typeProp: TypeProperty
            The property type to create the exploit for.
        @param getterProp: callable(object) -> object|None
            The getter used to get the value from the value object, if None provided it will use the received value.
        '''
        if typeProp.property == typeProp.container.propertyId:
            self.properties[typeProp.property] = self.encodeId(typeProp.type, getterProp)
        elif isinstance(typeProp.type, TypeModel):
            model = typeProp.type.container
            assert isinstance(model, Model)
            self.properties[typeProp.property] = self.encodeId(model.properties[model.propertyId], getterProp)
        else:
            self.properties[typeProp.property] = self.encodePrimitive(typeProp.type, getterProp)

    # ----------------------------------------------------------------

    def __call__(self, value, render, normalizer, **data):
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(render, IRender), 'Invalid render %s' % render

        if self.getterModel is not None: value = self.getterModel(value)
        if value is None: return
        data.update(value=value, render=render, normalizer=normalizer)

        render.objectStart(normalizer.normalize(self.name))
        for name, exploitProp in self.properties.items():
            exploitProp(name=normalizer.normalize(name), **data)
        render.objectEnd()
