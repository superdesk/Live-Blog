'''
Created on Jan 5, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for SQL alchemy service implementations.
'''

from .mapper import columnFor
from ally.internationalization import _, textdomain
from ally.api.configure import modelFor, queryFor
from ally.api.criteria import AsLike, AsOrdered, AsBoolean, AsEqual
from ally.api.operator import Query, CriteriaEntry
from ally.exception import InputException, Ref
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.schema import Column

# --------------------------------------------------------------------

textdomain('errors')

# --------------------------------------------------------------------

def handle(e, entity):
    '''
    Handles the SQL alchemy exception while inserting or updating.
    '''
    if isinstance(e, IntegrityError):
        raise InputException(Ref(_('Cannot persist, failed unique constraints on entity'), model=modelFor(entity)))
    if isinstance(e, OperationalError):
        raise InputException(Ref(_('A foreign key is not valid'), model=modelFor(entity)))
    raise e

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

def buildQuery(sqlQuery, query, queryClass=None):
    '''
    Builds the query on the SQL alchemy query.
    
    @param sqlQuery: SQL alchemy
        The sql alchemy query to use.
    @param query: query
        The REST query object to provide filtering on.
    @param queryClass: class
        The REST query class that represents the query object, is useful whenever the query object is in a basic
        form (not mapped).
    '''
    assert query is not None, 'A query object is required'
    if not queryClass:
        queryClass = query.__class__
    else:
        assert queryClass == query.__class__ or issubclass(queryClass, query.__class__), \
        'Invalid query %s for query class %s' % (query, queryClass)
    queryRest = queryFor(queryClass)
    assert isinstance(queryRest, Query), 'Invalid query %s, has no REST query' % queryRest
    for crtEnt in queryRest.criteriaEntries.values():
        assert isinstance(crtEnt, CriteriaEntry)
        if crtEnt.has(query):
            crt = crtEnt.get(query)
            column = columnFor(getattr(queryClass, crtEnt.name))
            assert isinstance(column, Column), 'No column available for %s' % getattr(queryClass, crtEnt.name)
            if isinstance(crt, AsBoolean):
                assert isinstance(crt, AsBoolean)
                if crt.flag is not None:
                    sqlQuery = sqlQuery.filter(column == crt.flag)
            elif isinstance(crt, AsLike):
                assert isinstance(crt, AsLike)
                if crt.like is not None:
                    if crt.caseInsensitive: sqlQuery = sqlQuery.filter(column.ilike(crt.like))
                    else: sqlQuery = sqlQuery.filter(column.like(crt.like))
            elif isinstance(crt, AsEqual):
                assert isinstance(crt, AsEqual)
                if crt.equal is not None:
                    sqlQuery = sqlQuery.filter(column == crt.equal)
            if isinstance(crt, AsOrdered):
                assert isinstance(crt, AsOrdered)
                if crt.orderAscending is not None:
                    if crt.orderAscending:
                        sqlQuery = sqlQuery.order_by(column)
                    else:
                        sqlQuery = sqlQuery.order_by(column.desc())
    return sqlQuery
