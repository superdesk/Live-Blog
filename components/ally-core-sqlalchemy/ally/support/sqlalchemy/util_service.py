'''
Created on Jan 5, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for SQL alchemy service implementations.
'''

from ally.api.criteria import AsLike, AsOrdered, AsBoolean, AsEqual, AsDate, \
    AsTime, AsDateTime, AsRange
from ally.api.operator.type import TypeCriteriaEntry
from ally.api.type import typeFor
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import namesForQuery, namesForModel
from ally.support.sqlalchemy.descriptor import PropertyAttribute
from itertools import chain
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.sql.expression import _Case

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
    if offset is not None: sqlQuery = sqlQuery.offset(offset)
    if limit is not None: sqlQuery = sqlQuery.limit(limit)
    return sqlQuery

def buildQuery(sqlQuery, query, mapped, only=None, exclude=None):
    '''
    Builds the query on the SQL alchemy query.

    @param sqlQuery: SQL alchemy
        The sql alchemy query to use.
    @param query: query
        The REST query object to provide filtering on.
    @param mapped: class
        The mapped model class to use the query on.
    @param only: tuple(string|TypeCriteriaEntry)|string|TypeCriteriaEntry|None
        The criteria names or references to build the query for, if no criteria is provided then all the query criteria
        are considered.
    @param exclude: tuple(string|TypeCriteriaEntry)|string|TypeCriteriaEntry|None
        The criteria names or references to be excluded when processing the query. If you provided a only parameter you cannot
        provide an exclude.
    '''
    assert query is not None, 'A query object is required'
    clazz = query.__class__

    columns, ordered, unordered = {}, [], []
    for name in namesForModel(mapped):
        cp, name = getattr(mapped, name), name.lower()
        if name not in columns and isinstance(cp, (PropertyAttribute, _Case)): columns[name] = cp
    columns = {criteria:columns.get(criteria.lower()) for criteria in namesForQuery(clazz)}

    if only:
        if not isinstance(only, tuple): only = (only,)
        assert not exclude, 'Cannot have only \'%s\' and exclude \'%s\' criteria at the same time' % (only, exclude)
        onlyColumns = {}
        for criteria in only:
            if isinstance(criteria, str):
                column = columns.get(criteria)
                assert column is not None, 'Invalid only criteria name \'%s\' for query class %s' % (criteria, clazz)
                onlyColumns[criteria] = column
            else:
                typ = typeFor(criteria)
                assert isinstance(typ, TypeCriteriaEntry), 'Invalid only criteria %s' % criteria
                column = columns.get(criteria)
                assert column is not None, 'Invalid only criteria \'%s\' for query class %s' % (criteria, clazz)
                onlyColumns[criteria] = column
        columns = onlyColumns
    elif exclude:
        if not isinstance(exclude, tuple): exclude = (exclude,)
        for criteria in exclude:
            if isinstance(criteria, str):
                column = columns.pop(criteria, None)
                assert column is not None, 'Invalid exclude criteria name \'%s\' for query class %s' % (criteria, clazz)
            else:
                typ = typeFor(criteria)
                assert isinstance(typ, TypeCriteriaEntry), 'Invalid exclude criteria %s' % criteria
                column = columns.pop(typ.name, None)
                assert column is not None, 'Invalid exclude criteria \'%s\' for query class %s' % (criteria, clazz)

    for criteria, column in columns.items():
        if column is None or getattr(clazz, criteria) not in query: continue

        crt = getattr(query, criteria)
        if isinstance(crt, AsBoolean):
            assert isinstance(crt, AsBoolean)
            if AsBoolean.value in crt:
                sqlQuery = sqlQuery.filter(column == crt.value)
        elif isinstance(crt, AsLike):
            assert isinstance(crt, AsLike)
            if AsLike.like in crt: sqlQuery = sqlQuery.filter(column.like(crt.like))
            elif AsLike.ilike in crt: sqlQuery = sqlQuery.filter(column.ilike(crt.ilike))
        elif isinstance(crt, AsEqual):
            assert isinstance(crt, AsEqual)
            if AsEqual.equal in crt:
                sqlQuery = sqlQuery.filter(column == crt.equal)
        elif isinstance(crt, (AsDate, AsTime, AsDateTime, AsRange)):
            if crt.__class__.start in crt: sqlQuery = sqlQuery.filter(column >= crt.start)
            elif crt.__class__.until in crt: sqlQuery = sqlQuery.filter(column < crt.until)
            if crt.__class__.end in crt: sqlQuery = sqlQuery.filter(column <= crt.end)
            elif crt.__class__.since in crt: sqlQuery = sqlQuery.filter(column > crt.since)

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


