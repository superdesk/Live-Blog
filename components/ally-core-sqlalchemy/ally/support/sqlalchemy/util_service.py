'''
Created on Jan 5, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for SQL alchemy service implementations.
'''

from ally.internationalization import _
from ally.api.criteria import AsLike, AsOrdered, AsBoolean, AsEqual
from ally.exception import InputError, Ref
from sqlalchemy.exc import IntegrityError, OperationalError
from ally.api.type import typeFor
from ally.api.operator.type import TypeQuery, TypeModel
from inspect import isclass
from ally.support.sqlalchemy.mapper_descriptor import MappedSupport
from ally.api.operator.container import Model
from itertools import chain

# --------------------------------------------------------------------

def handle(e, entity):
    '''
    Handles the SQL alchemy exception while inserting or updating.
    '''
    if isinstance(e, IntegrityError):
        raise InputError(Ref(_('Cannot persist, failed unique constraints on entity'), model=typeFor(entity).container))
    if isinstance(e, OperationalError):
        raise InputError(Ref(_('A foreign key is not valid'), model=typeFor(entity).container))
    raise e

# --------------------------------------------------------------------

def buildLimits(sqlQuery, offset=None, limit=None):
    '''
    Builds limiting on the SQL alchemy query.
    
    @param offset: integer|None
        The offset to fetch elements from.
    @param limit: integer|None
        The limit of elements to get.
    '''
    if offset: sqlQuery = sqlQuery.offset(offset)
    if limit: sqlQuery = sqlQuery.limit(limit)
    return sqlQuery

def buildQuery(sqlQuery, query, mapped):
    '''
    Builds the query on the SQL alchemy query.
    
    @param sqlQuery: SQL alchemy
        The sql alchemy query to use.
    @param query: query
        The REST query object to provide filtering on.
    @param mapped: class
        The mapped model class to use the query on.
    '''
    assert query is not None, 'A query object is required'
    clazz = query.__class__
    queryType = typeFor(clazz)
    assert isinstance(queryType, TypeQuery), 'Invalid query %s' % query
    assert isclass(mapped), 'Invalid class %s' % mapped
    assert isinstance(mapped, MappedSupport), 'Invalid mapped class %s' % mapped
    modelType = typeFor(mapped)
    assert isinstance(modelType, TypeModel), 'Invalid model class %s' % mapped
    model = modelType.container
    assert isinstance(model, Model)

    ordered, unordered = [], []
    properties = {prop.lower(): getattr(mapped, prop) for prop in model.properties}
    for criteria in queryType.query.criterias:
        column = properties.get(criteria.lower())
        if column is not None and getattr(clazz, criteria) in query:
            crt = getattr(query, criteria)
            if isinstance(crt, AsBoolean):
                assert isinstance(crt, AsBoolean)
                if AsBoolean.value in crt:
                    sqlQuery = sqlQuery.filter(column == crt.value)
            elif isinstance(crt, AsLike):
                assert isinstance(crt, AsLike)
                if AsLike.like in crt:
                    if crt.caseInsensitive: sqlQuery = sqlQuery.filter(column.ilike(crt.like))
                    else: sqlQuery = sqlQuery.filter(column.like(crt.like))
            elif isinstance(crt, AsEqual):
                assert isinstance(crt, AsEqual)
                if AsEqual.equal in crt:
                    sqlQuery = sqlQuery.filter(column == crt.equal)
            if isinstance(crt, AsOrdered):
                assert isinstance(crt, AsOrdered)
                if AsOrdered.ascending in crt:
                    if AsOrdered.priority in crt and crt.priority:
                        ordered.append((column, crt.ascending, crt.priority))
                    else:
                        unordered.append((column, crt.ascending, None))

            ordered.sort(key=lambda pack: pack[2])
            for column, asc, __ in chain(ordered, unordered):
                if asc: sqlQuery = sqlQuery.order_by(column)
                else: sqlQuery = sqlQuery.order_by(column.desc())

    return sqlQuery

# --------------------------------------------------------------------
