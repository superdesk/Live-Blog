'''
Created on Jan 5, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides helper functions for SQL alchemy.
'''

from .mapper import columnFor
from ally.api.configure import modelFor, queryFor
from ally.api.criteria import AsLike, AsOrdered, AsBoolean
from ally.api.operator import Query, CriteriaEntry
from ally.exception import InputException, Ref
from inspect import isclass
from sqlalchemy.exc import IntegrityError, OperationalError

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

def buildLimits(aq, offset=None, limit=None):
    '''
    Builds limiting on the SQL alchemy query.
    '''
    if offset: aq = aq.offset(offset)
    if limit: aq = aq.limit(limit)
    return aq

def buildQuery(aq, query, q):
    '''
    Builds the query on the SQL alchemy query.
    '''
    if isclass(query): query = queryFor(query)
    assert isinstance(query, Query), 'Invalid query %s' % query
    for crtEnt in query.criteriaEntries.values():
        assert isinstance(crtEnt, CriteriaEntry)
        if crtEnt.has(q):
            crt = crtEnt.get(q)
            if isinstance(crt, AsBoolean):
                assert isinstance(crt, AsBoolean)
                if crt.flag is not None:
                    aq = aq.filter(columnFor(crtEnt) == crt.flag)
            if isinstance(crt, AsLike):
                assert isinstance(crt, AsLike)
                if crt.like is not None:
                    if crt.caseInsensitive: aq = aq.filter(columnFor(crtEnt).ilike(crt.like))
                    else: aq = aq.filter(columnFor(crtEnt).like(crt.like))
            if isinstance(crt, AsOrdered):
                assert isinstance(crt, AsOrdered)
                if crt.orderAscending is not None:
                    if crt.orderAscending:
                        aq = aq.order_by(columnFor(crtEnt))
                    else:
                        aq = aq.order_by(columnFor(crtEnt).desc())
    return aq
