'''
Created on Jan 4, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy mapper that is able to link the alchemy with REST models.
'''

from abc import ABCMeta
from ally.api.operator.container import Model
from ally.api.operator.descriptor import ContainerSupport, Reference
from ally.api.operator.type import TypeModel, TypeModelProperty
from ally.api.type import typeFor
from ally.container.binder import indexAfter
from ally.container.binder_op import INDEX_PROP, validateAutoId, \
    validateRequired, validateMaxLength, validateProperty, validateManaged
from ally.exception import Ref
from ally.internationalization import _
from ally.support.sqlalchemy.descriptor import PropertyAttribute, PropertyHybrid, \
    PropertyAssociation
from ally.support.sqlalchemy.session import openSession
from ally.support.util_sys import getAttrAndClass
from collections import deque
from functools import partial
from inspect import isclass
from sqlalchemy import event
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.schema import Table, MetaData, Column, ForeignKey
from sqlalchemy.sql.expression import Join
from sqlalchemy.types import String
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

INDEX_PROP_FK = indexAfter('propFk', INDEX_PROP)
# Index for foreign key properties

# --------------------------------------------------------------------

class MappingError(Exception):
    '''
    Provides the exception used whenever a mapping issue occurs.
    '''

# --------------------------------------------------------------------

def mapperSimple(clazz, sql, **keyargs):
    '''
    Maps a table to a ally REST model. Use this instead of the classical SQL alchemy mapper since this will
    also provide to the model additional information extracted from the SQL alchemy configurations.
    
    @param clazz: class
        The model class to be mapped with the provided sql.
    @param sql: Table|Join|Select
        The table or join to map the model with.
    @param keyargs: key arguments
        This key arguments are directly delivered to the SQL alchemy @see mapper.
    @return: class
        The obtained mapped class.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    if isinstance(sql, Table):
        metadata = sql.metadata
    elif isinstance(sql, Join):
        metadata = keyargs.pop('metadata', None)
        assert metadata is not None, \
        'For a join mapping you need to specify the metadata in the key words arguments \'metadata=?\''
    else:
        raise MappingError('Invalid sql source %s' % sql)
    assert isinstance(metadata, MetaData), 'Invalid metadata %s' % metadata

    inherits = keyargs.pop('inherits', None)

    attributes = {'__module__': clazz.__module__}
    attributes['__table__'] = sql
    attributes['metadata'] = metadata
    if keyargs: attributes['__mapper_args__'] = keyargs

    # We need to treat the case when a model inherits another, since the provided inherited model class is actually the 
    # mapped class the provided model class will not be seen as inheriting the provided mapped class
    if inherits is not None:
        assert isclass(inherits), 'Invalid class %s' % inherits
        if __debug__:
            assert issubclass(inherits, ContainerSupport), 'Invalid model inheritance class %s' % inherits
            assert isinstance(inherits, MappedSupport), 'Invalid inherit class %s, is not mapped' % inherits
        bases = (inherits, clazz)
    else:
        try: Base = metadata._ally_mapper_base
        except AttributeError:
            Base = metadata._ally_mapper_base = declarative_base(metadata=metadata, metaclass=DeclarativeMetaModel)
        bases = (Base, clazz)

    return type(clazz.__name__ + '$Mapped', bases, attributes)

def mapperModel(clazz, sql, exclude=None, **keyargs):
    '''
    Maps a table to a ally REST model. Use this instead of the classical SQL alchemy mapper since this will
    also provide to the model additional information extracted from the SQL alchemy configurations. Use
    this mapper to also add validations for updating and inserting on the model.
    
    @param clazz: class
        The model class to be mapped with the provided sql table.
    @param sql: Table|Join|Select
        The table or join to map the model with.
    @param exclude: list[string]|tuple(string)
        A list of column names to be excluded from automatic validation.
    @param keyargs: key arguments
        This key arguments are directly delivered to the SQL alchemy @see mapper.  
    @return: class
        The mapped class, basically a model derived class that also contains the mapping data.
    '''
    mapped = mapperSimple(clazz, sql, **keyargs)
    registerValidation(mapped, exclude=exclude)

    return mapped

# --------------------------------------------------------------------

class DeclarativeMetaModel(DeclarativeMeta):
    '''
    Extension for @see: DeclarativeMeta class that provides also the merging with the API model.
    '''

    def __new__(cls, name, bases, namespace):
        namespace['_ally_type'] = None # Makes the type None in order to avoid mistakes by inheriting the type from a model
        return DeclarativeMeta.__new__(cls, name, bases, namespace)

    def __init__(self, name, bases, namespace):
        assert isinstance(namespace, dict), 'Invalid namespace %s' % namespace

        mapped, models = [], []
        for cls in bases:
            typ = typeFor(cls)
            if isinstance(typ, TypeModelMapped): mapped.append(cls)
            elif isinstance(typ, TypeModel): models.append(cls)

        if not mapped and not models:
            assert log.debug('Cannot find any API model class for \'%s\', no merging required', name) or True
            DeclarativeMeta.__init__(self, name, bases, namespace)
            return

        if len(mapped) > 1: raise MappingError('Cannot inherit more then one mapped class, got %s' % models)

        if len(models) > 1: raise MappingError('Cannot merge with more then one API model class, got %s' % models)

        if models: typeModel = typeFor(models[0])
        else: typeModel = None
        if mapped:
            if typeModel is None: typeModel = typeFor(mapped[0]).base
        assert isinstance(typeModel, TypeModel)
        typeModel = TypeModelMapped(self, typeModel)

        self._ally_reference = {prop: Reference(TypeModelProperty(typeModel, prop, propType))
                                for prop, propType in typeModel.container.properties.items()}
        self._ally_listeners = {} # Provides the BindableSupport
        self._ally_type = typeModel # Provides the TypeSupport

        DeclarativeMeta.__init__(self, name, bases, namespace)

        #TODO: see if required: self.__clause_element__ = lambda: self.__table__

        for prop in typeModel.container.properties:
            if typeFor(getattr(self, prop)) != typeFor(self._ally_reference[prop]):
                value, _class = getAttrAndClass(self, prop)
                setattr(self, prop, value)

        try: mappings = self.metadata._ally_mappers
        except AttributeError: mappings = self.metadata._ally_mappers = deque()
        mappings.append(self)

    def __setattr__(self, key, value):
        '''
        @see: DeclarativeMeta.__setattr__
        '''
        if self._ally_type is not None and key in self._ally_type.container.properties:
            typeProperty = typeFor(self._ally_reference[key])

            if isinstance(value, InstrumentedAttribute): value = PropertyAttribute(typeProperty, value)
            elif isinstance(value, hybrid_property): value = PropertyHybrid(typeProperty, value)
            elif isinstance(value, AssociationProxy): value = PropertyAssociation(typeProperty, value)

        super().__setattr__(key, value)

# --------------------------------------------------------------------

def validate(*args, exclude=None):
    '''
    Decorator used for validating declarative based mapped classes, same as @see:  registerValidation
    '''
    if not args: return partial(validate, exclude=exclude)
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz
    registerValidation(clazz, exclude)
    return clazz

def registerValidation(mapped, exclude=None):
    '''
    Register to mapped class all the validations that can be performed based on the SQL alchemy mapping.
    
    @param mapped: class
        The mapped model class.
    @param exclude: list[string]|tuple(string)
        A list of column names to be excluded from automatic validation.
    @return: Property
        The property id of the model.
    '''
    assert isclass(mapped), 'Invalid class %s' % mapped
    mapper, typeModel = mappingFor(mapped), typeFor(mapped)
    assert isinstance(mapper, Mapper), 'Invalid mapped class %s' % mapped
    assert isinstance(typeModel, TypeModel), 'Invalid model class %s' % mapped
    assert not exclude or isinstance(exclude, (list, tuple)), 'Invalid exclude %s' % exclude
    model = typeModel.container
    assert isinstance(model, Model)

    properties = set(model.properties)
    for cp in mapper.iterate_properties:
        if not isinstance(cp, ColumnProperty): continue

        assert isinstance(cp, ColumnProperty)
        if cp.key:
            prop = cp.key
            try: properties.remove(prop)
            except KeyError: continue

            if not (exclude and prop in exclude):
                propRef = getattr(mapped, prop)
                column = getattr(mapper.c, cp.key, None)
                assert isinstance(column, Column), 'Invalid column %s' % column
                if __debug__:
                    propType = typeFor(propRef)
                    assert isinstance(propType, TypeModelProperty), 'Invalid property %s with type %s' % (prop, propType)

                if column.primary_key and column.autoincrement:
                    if prop != model.propertyId:
                        raise MappingError('The primary key is expected to be %s, but got SQL primary key for %s' %
                                           (model.propertyId, prop))
                    validateAutoId(propRef)
                elif not column.nullable:
                    validateRequired(propRef)

                if isinstance(column.type, String) and column.type.length:
                    validateMaxLength(propRef, column.type.length)
                if column.unique:
                    validateProperty(propRef, partial(onPropertyUnique, mapped))
                if column.foreign_keys:
                    for fk in column.foreign_keys:
                        assert isinstance(fk, ForeignKey)
                        try: fkcol = fk.column
                        except AttributeError:
                            raise MappingError('Invalid foreign column for %s, maybe you are not using the meta class'
                                               % prop)
                        validateProperty(propRef, partial(onPropertyForeignKey, mapped, fkcol), index=INDEX_PROP_FK)

    for prop in properties:
        if not (exclude and prop in exclude): validateManaged(getattr(mapped, prop))

def mappingFor(mapped):
    '''
    Provides the mapper of the provided mapped class.
    
    @param mapped: class
        The mapped class.
    @return: Mapper
        The associated mapper.
    '''
    assert isinstance(mapped, DeclarativeMetaModel), 'Invalid mapped class %s' % mapped

    return mapped.__mapper__

def mappingsOf(metadata):
    '''
    Provides the mapping dictionary of the provided meta.
    
    @param metadata: MetaData
        The meta to get the mappings for.
    @return: dictionary{class,class}
        A dictionary containing as a key the model API class and as a value the mapping class for the model.
    '''
    assert isinstance(metadata, MetaData), 'Invalid meta data %s' % metadata

    try: mappings = metadata._ally_mappers
    except AttributeError: return {}

    return {typeFor(mapped).base.clazz:mapped for mapped in mappings}

# --------------------------------------------------------------------

def onPropertyUnique(mapped, prop, obj, errors):
    '''
    Validation of a sql alchemy unique property.
    
    @param mapped: class
        The mapped model class.
    @param prop: string
        The property name to be checked if unique.
    @param obj: object
        The entity to check for the property value.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isclass(mapped), 'Invalid class %s' % mapped
    assert isinstance(prop, str), 'Invalid property name %s' % prop
    assert obj is not None, 'None is not a valid object'
    assert isinstance(errors, list), 'Invalid errors list %s' % errors

    propRef = getattr(mapped, prop)
    if propRef in obj:
        try:
            db = openSession().query(mapped).filter(propRef == getattr(obj, prop)).one()
        except NoResultFound:
            return
        propId = typeFor(mapped).container.propertyId
        if getattr(obj, propId) != getattr(db, propId):
            errors.append(Ref(_('Already an entry with this value'), ref=propRef))
            return False

def onPropertyForeignKey(mapped, foreignColumn, prop, obj, errors):
    '''
    Validation of a sql alchemy fpreign key property.
    
    @param mapped: class
        The mapped model class.
    @param foreignColumn: Column
        The foreign column used for checking.
    @param prop: string
        The property name tthat contains the foreign key.
    @param obj: object
        The entity to check for the property value.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isclass(mapped), 'Invalid class %s' % mapped
    assert isinstance(foreignColumn, Column), 'Invalid foreign column %s' % foreignColumn
    assert isinstance(prop, str), 'Invalid property name %s' % prop
    assert obj is not None, 'None is not a valid object'
    assert isinstance(errors, list), 'Invalid errors list %s' % errors

    propRef = getattr(mapped, prop)
    if propRef in obj:
        val = getattr(obj, prop)
        if val is not None:
            count = openSession().query(foreignColumn).filter(foreignColumn == val).count()
            if count == 0:
                errors.append(Ref(_('Unknown foreign id'), ref=propRef))
                return False

# --------------------------------------------------------------------

def addLoadListener(mapped, listener):
    '''
    Adds a load listener that will get notified every time the mapped class entity is loaded.
    
    @param mapped: class
        The model mapped class to add the listener to.
    @param listener: callable(object)
        A function that has to take as parameter the model instance that has been loaded.
    '''
    assert isclass(mapped), 'Invalid class %s' % mapped
    assert callable(listener), 'Invalid listener %s' % listener
    def onLoad(target, *args): listener(target)
    event.listen(mapped, 'load', onLoad)

def addInsertListener(mapped, listener, before=True):
    '''
    Adds an insert listener that will get notified every time the mapped class entity is inserted.
    
    @param mapped: class
        The model mapped class to add the listener to.
    @param listener: callable(object)
        A function that has to take as parameter the model instance that will be or has been inserted.
    @param before: boolean
        If True the listener will be notified before the insert occurs, if False will be notified after.
    '''
    assert isclass(mapped), 'Invalid class %s' % mapped
    assert isinstance(mapped, MappedSupport), 'Invalid mapped class %s' % mapped
    assert callable(listener), 'Invalid listener %s' % listener
    assert isinstance(before, bool), 'Invalid before flag %s' % before
    def onInsert(mapper, conn, target): listener(target)
    if before: event.listen(mapped.__mapper__, 'before_insert', onInsert)
    else: event.listen(mapped.__mapper__, 'after_insert', onInsert)

def addUpdateListener(mapped, listener, before=True):
    '''
    Adds an update listener that will get notified every time the mapped class entity is update.
    
    @param mapped: class
        The model mapped class to add the listener to.
    @param listener: callable(object)
        A function that has to take as parameter the model instance that will be or has been update.
    @param before: boolean
        If True the listener will be notified before the update occurs, if False will be notified after.
    '''
    assert isclass(mapped), 'Invalid class %s' % mapped
    assert isinstance(mapped, MappedSupport), 'Invalid mapped class %s' % mapped
    assert callable(listener), 'Invalid listener %s' % listener
    assert isinstance(before, bool), 'Invalid before flag %s' % before
    def onUpdate(mapper, conn, target): listener(target)
    if before: event.listen(mapped.__mapper__, 'before_update', onUpdate)
    else: event.listen(mapped.__mapper__, 'after_update', onUpdate)

# --------------------------------------------------------------------

class TypeModelMapped(TypeModel):
    '''
    A @see: TypeModel extension for mapped models.
    '''

    __slots__ = ('base',)

    def __init__(self, clazz, base):
        '''
        Construct the mapped type model based on the provided base type model.
        
        @param base: TypeModel
            The base type model for this mapped model
        '''
        assert isinstance(base, TypeModel), 'Invalid base type model %s' % base
        assert not isinstance(base, TypeModelMapped), 'Invalid base type model %s, is already a mapped type' % base
        TypeModel.__init__(self, clazz, base.container)

        self.base = base

    def isOf(self, type):
        '''
        @see: Type.isOf
        '''
        return super().isOf(type) or self.base.isOf(type)

    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        return super().isValid(obj) or self.base.isValid(obj)

# --------------------------------------------------------------------

class MappedSupportMeta(ABCMeta):
    '''
    Meta class for mapping support that allows for instance check base on the '__mapper__' attribute.
    '''

    def __instancecheck__(self, instance):
        '''
        @see: ABCMeta.__instancecheck__
        '''
        if ABCMeta.__instancecheck__(self, instance): return True
        if self is not MappedSupport: return False
        return isinstance(getattr(instance, '__mapper__', None), Mapper)

class MappedSupport(metaclass=MappedSupportMeta):
    '''
    Support class for mapped classes.
    '''
    __mapper__ = Mapper # Contains the mapper that represents the model

# --------------------------------------------------------------------
#TODO: check if is still a problem in the new SQL alchemy version
# This is a fix for the aliased models.
def adapted(self, adapter):
    '''
    @see: InstrumentedAttribute.adapted
    We need to adjust this in order to be able to alias.
    '''
    adapted = InstrumentedAttribute(self.prop, self.mapper, adapter)
    adapted.comparator = self.comparator.adapted(adapter)
    adapted.class_ = self.class_
    return adapted
InstrumentedAttribute.adapted = adapted
