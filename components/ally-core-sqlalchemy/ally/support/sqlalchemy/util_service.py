'''
Created on Jan 5, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for SQL alchemy service implementations.
'''

from .mapper import columnFor
from ally import internationalization
from ally.api.configure import modelFor, queryFor
from ally.api.criteria import AsLike, AsOrdered, AsBoolean
from ally.api.operator import Query, CriteriaEntry
from ally.exception import InputException, Ref
from sqlalchemy.exc import IntegrityError, OperationalError

# --------------------------------------------------------------------

_ = internationalization.translator(__name__)

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

def buildQuery(sqlQuery, query):
    '''
    Builds the query on the SQL alchemy query.
    
    @param sqlQuery: SQL alchemy
        The sql alchemy query to use.
    @param query: query
        The REST query object to provide filtering on.
    '''
    queryRest = queryFor(query)
    assert isinstance(queryRest, Query), 'Invalid query %s, has no REST query' % queryRest
    for crtEnt in queryRest.criteriaEntries.values():
        assert isinstance(crtEnt, CriteriaEntry)
        if crtEnt.has(query):
            crt = crtEnt.get(query)
            if isinstance(crt, AsBoolean):
                assert isinstance(crt, AsBoolean)
                if crt.flag is not None:
                    sqlQuery = sqlQuery.filter(columnFor(crtEnt) == crt.flag)
            if isinstance(crt, AsLike):
                assert isinstance(crt, AsLike)
                if crt.like is not None:
                    if crt.caseInsensitive: sqlQuery = sqlQuery.filter(columnFor(crtEnt).ilike(crt.like))
                    else: sqlQuery = sqlQuery.filter(columnFor(crtEnt).like(crt.like))
            if isinstance(crt, AsOrdered):
                assert isinstance(crt, AsOrdered)
                if crt.orderAscending is not None:
                    if crt.orderAscending:
                        sqlQuery = sqlQuery.order_by(columnFor(crtEnt))
                    else:
                        sqlQuery = sqlQuery.order_by(columnFor(crtEnt).desc())
    return sqlQuery
