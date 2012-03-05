'''
Created on Jan 4, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy mapper that is able to link the alchemy with REST models.
'''

from ..util import Attribute
from .session import openSession
from ally.internationalization import _, textdomain
from ally.api.configure import modelFor, queryFor
from ally.api.operator import Model, Property, Query, CriteriaEntry
from ally.api.type import typeFor
from ally.exception import Ref
from ally.listener.binder import indexAfter
from ally.listener.binder_op import validateAutoId, validateRequired, \
    validateMaxLength, validateProperty, validateManaged, validateModelProperties, \
    INDEX_PROP, createQueryMapping, createModelMapping
from inspect import isclass
from sqlalchemy import event
from sqlalchemy.orm import mapper
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.schema import Table, Column, ForeignKey, MetaData
from sqlalchemy.sql.expression import Join
from sqlalchemy.types import String
import functools

# --------------------------------------------------------------------

INDEX_PROP_FK = indexAfter('propFk', INDEX_PROP)
# Index for foreign key properties

textdomain('error')

# --------------------------------------------------------------------

class MappingError(Exception):
    '''
    Provides the exception used whenever a mapping issue occurs.
    '''

# --------------------------------------------------------------------

def mapperSimple(modelClass, sql, **keyargs):
    '''
    Maps a table to a ally REST model. Use this instead of the classical SQL alchemy mapper since this will
    also provide to the model additional information extracted from the SQL alchemy configurations.
    
    @param modelClass: class
        The model class to be mapped with the provided sql table.
    @param sql: Table|Join|Select
        The table or join to map the model with.
    @param keyargs: key arguments
        This key arguments are directly delivered to the SQL alchemy @see mapper.
    @return: class
        The obtained mapped class.
    '''
    assert isclass(modelClass), 'Invalid model class %s' % modelClass
    model = modelFor(modelClass)
    assert isinstance(model, Model), 'Invalid class %s is not a model' % modelClass
    assert mapperFor(modelClass) is None, 'The class %s is already mapped ' % modelClass
    assert isinstance(sql, Table) or isinstance(sql, Join), 'Invalid SQL alchemy table/join %s' % sql
    
    mappedClass = createModelMapping(modelClass)
    mapper_ = mapperFor(mappedClass, mapper(mappedClass, sql, **keyargs))
    mappings = mappingsOf(mapper_.tables[0].metadata)
    assert model not in mappings, 'The model %s is already mapped' % model
    mappings[modelClass] = mappedClass
    
    for name, typ in model.typeProperties.items():
        col = getattr(mappedClass, name, None)
        if col is not None:
            if typeFor(col) is None: typeFor(col, typ)
            mapperFor(col, mapper_)
            mappedClassFor(col, mappedClass)

    event.listen(mapper_, 'load', _eventLoad)
    event.listen(mapper_, 'after_insert', _eventInsert)
    
    return mappedClass

def mapperModelProperties(mappedClass, exclude=None):
    '''
    Maps the model class properties to the provided SQL alchemy mapping.
    
    @param modelClass: class
        The mapped model class.
    @param exclude: list[string]|tuple(string)
        A list of column names to be excluded from automatic validation.
    @return: Property
        The property id of the model.
    '''
    assert isclass(mappedClass), 'Invalid mapped model class %s' % mappedClass
    model = modelFor(mappedClass)
    assert isinstance(model, Model), 'Invalid class %s is not a model' % mappedClass
    mapper = mapperFor(mappedClass)
    assert isinstance(mapper, Mapper), 'Invalid mapped class %s, no mapper present' % mappedClass
    assert not exclude or isinstance(exclude, (list, tuple)), 'Invalid exclude %s' % exclude
    
    properties, propertyId = dict(model.properties), None
    for cp in mapper.iterate_properties:
        assert isinstance(cp, ColumnProperty)
        if cp.key:
            prop = properties.pop(cp.key, None)
            if prop:
                assert isinstance(prop, Property)
                propMapping = getattr(mappedClass, prop.name)
                
                isExclude = False if exclude is None else prop.name in exclude
                column = cp.columns[0]
                assert isinstance(column, Column), 'Invalid column %s' % column
                #TODO: add checking if the column type is the same with the property, meaning that the alchemy
                # specification is same with REST
                if column.primary_key and column.autoincrement:
                    if propertyId:
                        raise MappingError('Found another property id %s for model %s' % (prop, model))
                    propertyId = prop
                if not isExclude:
                    if propertyId == prop: validateAutoId(propMapping)
                    elif not column.nullable: validateRequired(propMapping)
                    if isinstance(column.type, String) and column.type.length:
                        validateMaxLength(propMapping, column.type.length)
                    if column.unique: validateProperty(propMapping, onPropertyUnique)
                    if column.foreign_keys:
                        for fk in column.foreign_keys:
                            assert isinstance(fk, ForeignKey)
                            try: fkcol = fk.column
                            except AttributeError:
                                raise MappingError('Invalid foreign column for %s, maybe you are not using the meta class' 
                                                   % prop)
                            validateProperty(propMapping, functools.partial(onPropertyForeignKey, fkcol),
                                             index=INDEX_PROP_FK)
    if not propertyId: raise MappingError('No id found for model %s' % model)
    propertyIdFor(mappedClass, propertyId)
    
    for prop in properties.values():
        if exclude is None or prop.name not in exclude: validateManaged(getattr(mappedClass, prop.name))
    
    validateModelProperties(mappedClass)
    
    return propertyId

def mapperModel(modelClass, sql, exclude=None, **keyargs):
    '''
    Maps a table to a ally REST model. Use this instead of the classical SQL alchemy mapper since this will
    also provide to the model additional information extracted from the SQL alchemy configurations. Use
    this mapper to also add validations for updating and inserting on the model.
    
    @param modelClass: class
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
    mappedClass = mapperSimple(modelClass, sql, **keyargs)
    mapperModelProperties(mappedClass, exclude=exclude)
    
    return mappedClass

# --------------------------------------------------------------------

def mapperQuery(queryClass, sql):
    '''
    Maps a table to a ally REST query. This will provide the ability to use the 
    
    @param queryClass: class
        The query class to be mapped with the provided sql table.
    @param sql: Table|Join|Mapped Model
        The table, join or a mapped model class to map the query with.
    '''
    assert isclass(queryClass), 'Invalid query class %s' % queryClass
    if isinstance(modelFor(sql), Model):
        sql = mapperFor(sql)
        assert isinstance(sql, Mapper), 'Invalid mapped model %s, no mapper present' % sql
    if isinstance(sql, Mapper):
        columns = [(cp.key, cp.columns[0]) for cp in sql.iterate_properties if cp.key]
    else:
        assert isinstance(sql, Table) or isinstance(sql, Join), 'Invalid SQL alchemy table/join %s' % sql
        columns = [(column.key, column) for column in sql.columns if column.key]
        
    query = queryFor(queryClass)
    assert isinstance(query, Query), 'Invalid class %s is not a query' % queryClass
    criteriaEntries = {name.lower():crtEntry for name, crtEntry in query.criteriaEntries.items()}
    
    mappedClass = createQueryMapping(queryClass)
    for name, column in columns:
        assert isinstance(column, Column)
        crtEntry = criteriaEntries.get(name.lower(), None)
        if crtEntry:
            assert isinstance(crtEntry, CriteriaEntry)
            mapping = getattr(mappedClass, crtEntry.name, None)
            if mapping is not None:
                if typeFor(mapping) is None: typeFor(mapping, query.typeCriteriaEntries[name])
                columnFor(mapping, column)
        
    return mappedClass

# --------------------------------------------------------------------

def onPropertyUnique(entity, mappedClass, prop, errors):
    '''
    Validation of a sql alchemy unique property.
    
    @param entity: object
        The entity to check for the property value.
    @param mappedClass: class
        The model mapped class of the entity.
    @param prop: Property
        The property that is unwanted.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
    model = modelFor(mappedClass)
    assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % mappedClass
    assert isinstance(entity, model.modelClass), 'Invalid entity %s for model %s' % (entity, model)
    propertyId = propertyIdFor(mappedClass)
    assert isinstance(propertyId, Property), 'Cannot find any property id for class %s' % mappedClass
    assert isinstance(prop, Property), 'Invalid property %s' % prop
    assert isinstance(errors, list), 'Invalid errors list %s' % errors
    if prop.has(entity):
        column = getattr(mappedClass, prop.name)
        try:
            db = openSession().query(mappedClass).filter(column == prop.get(entity)).one()
        except NoResultFound: return
        if propertyId.get(db) != propertyId.get(entity):
            errors.append(Ref(_('Already an entry with this value'), ref=column))
            return False
    
def onPropertyForeignKey(foreignColumn, entity, mappedClass, prop, errors):
    '''
    Validation of a sql alchemy fpreign key property.
    
    @param foreignColumn: Column
        The foreign column used for checking.
    @param entity: object
        The entity to check for the property value.
    @param mappedClass: class
        The model mapped class of the entity.
    @param prop: Property
        The property that is unwanted.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isinstance(foreignColumn, Column), 'Invalid foreign column %s' % foreignColumn
    assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
    model = modelFor(mappedClass)
    assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % mappedClass
    assert isinstance(entity, model.modelClass), 'Invalid entity %s for model %s' % (entity, model)
    assert isinstance(prop, Property), 'Invalid property %s' % prop
    assert isinstance(errors, list), 'Invalid errors list %s' % errors
    if prop.has(entity):
        val = prop.get(entity)
        if val is not None:
            count = openSession().query(foreignColumn).filter(foreignColumn == val).count()
            if count == 0:
                errors.append(Ref(_('Unknown foreign id'), model=modelFor(mappedClass), property=prop))
                return False
        
# --------------------------------------------------------------------

def addLoadListener(mappedClass, listener):
    '''
    Adds a load listener that will get notified every time a entity is loaded.
    
    @param mappedClass: class
        The model mapped class to add the listener to.
    @param listener: callable(object)
        A function that has to take as parameter the model instance that has been loaded.
    '''
    assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
    def onLoad(target, *args): listener(target)
    event.listen(mappedClass, 'load', onLoad)

ATTR_SQL_MAPPINGS = Attribute(__name__, 'mappings', dict)
# Attribute used to store the meta mappings.
def mappingsOf(meta):
    '''
    Provides the mapping dictionary of the provided meta.
    
    @param meta: MetaData
        The meta to get the mappings for.
    @return: dictionary{class,class}
        A dictionary containing as a key the model API class and as a value the mapping class for the model.
    '''
    assert isinstance(meta, MetaData), 'Invalid meta %s' % meta
    if ATTR_SQL_MAPPINGS.hasOwn(meta): return ATTR_SQL_MAPPINGS.get(meta)
    return ATTR_SQL_MAPPINGS.set(meta, {})
    

ATTR_SQL_MAPPER = Attribute(__name__, 'mapper', Mapper)
# Attribute used to store the mapper.
def mapperFor(obj, mapper=None):
    '''
    If the mapper is provided it will be associate with the obj, if the mapper is not provided than this function
    will try to provide if it exists the mapper associated with the obj, or check if the obj is not a mapper itself and
    provide that.
    
    @param obj: object
        The class to associate or extract the mapper.
    @param mapper: Mapper|None
        The mapper to associate with the obj.
    @return: Mapper|None
        If the mapper has been associate then the return will be the associated mapper, if the mapper is being extracted 
        it can return either the Mapper or None if is not found.
    '''
    if mapper is None:
        if isinstance(obj, Mapper): return obj
        return ATTR_SQL_MAPPER.get(obj, None)
    assert not ATTR_SQL_MAPPER.hasOwn(obj), 'Already has a mapper %s' % obj
    return ATTR_SQL_MAPPER.set(obj, mapper)

ATTR_SQL_MAPPED = Attribute(__name__, 'mapped', type)
# Attribute used to store the mapped class.
def mappedClassFor(obj, mappedClass=None):
    '''
    If the mapped class is provided it will be associate with the obj, if the mapped class is not provided than this 
    function will try to provide if it exists the mapped class associated with the obj, or check if the obj is not a
    mapped class itself and provide that.
    
    @param obj: object
        The class to associate or extract the mapped class.
    @param mappedClass: class|None
        The mapped class to associate with the obj.
    @return: class|None
        If the mapped class has been associate then the return will be the associated mapped class, if the mapped class
        is being extracted it can return either the mapped class or None if is not found.
    '''
    if mappedClass is None:
        if isclass(obj): return obj
        return ATTR_SQL_MAPPED.get(obj, None)
    assert not ATTR_SQL_MAPPED.hasOwn(obj), 'Already has a mapped class %s' % obj
    return ATTR_SQL_MAPPED.set(obj, mappedClass)

ATTR_SQL_PROPERTY_ID = Attribute(__name__, 'propertyId', Property)
# Attribute used to store the property id.
def propertyIdFor(obj, propertyId=None):
    '''
    If the property id is provided it will be associate with the obj, if the property id is not provided than this 
    function will try to provide if it exists the property id associated with the obj, or check if the obj.
    
    @param obj: object
        The class to associate or extract the property id.
    @param propertyId: Property|None
        The property id to associate with the obj.
    @return: Property|None
        If the property id has been associate then the return will be the associated property id, if the property id is
        being extracted it can return either the property id or None if is not found.
    '''
    if propertyId is None: return ATTR_SQL_PROPERTY_ID.get(obj, None)
    assert not ATTR_SQL_PROPERTY_ID.hasOwn(obj), 'Already has a property id %s' % obj
    return ATTR_SQL_PROPERTY_ID.set(obj, propertyId)

ATTR_SQL_COLUMN = Attribute(__name__, 'column', Column)
# Attribute used to store the column.
def columnFor(obj, column=None):
    '''
    If the column is provided it will be associate with the obj, if the column is not provided than this function
    will try to provide if it exists the column associated with the obj, or check if the obj is not a column itself and
    provide that.
    
    @param obj: object
        The class to associate or extract the mapper.
    @param column: Column|None
        The column to associate with the obj.
    @return: Column|None
        If the column has been associate then the return will be the associated column, if the column is being extracted 
        it can return either the column or None if is not found.
    '''
    if column is None:
        if isinstance(obj, Column): return obj
        return ATTR_SQL_COLUMN.get(obj, None)
    assert not ATTR_SQL_COLUMN.hasOwn(obj), 'Already has a column %s' % obj
    return ATTR_SQL_COLUMN.set(obj, column)

# --------------------------------------------------------------------

def _eventDBUpdate(targetIndex, *args):
    '''
    FOR INTERNAL USE!
    Listener method called when an database mapped instance is updated by SQL alchemy. This will change on the target
    entity the has set flag for all properties that have a value.
    '''
    target = args[targetIndex]
    model = modelFor(target)
    if model:
        assert isinstance(model, Model)
        for name, prop in model.properties.items():
            if name in target.__dict__:
                assert isinstance(prop, Property)
                if not prop.has(target): prop.hasSet(target)

_eventLoad = functools.partial(_eventDBUpdate, 0)
# FOR INTERNAL USE! listener method called when an database mapped instance is loaded by SQL alchemy.
_eventInsert = functools.partial(_eventDBUpdate, 2)
# FOR INTERNAL USE! listener method called when an database mapped instance is inserted by SQL alchemy.
