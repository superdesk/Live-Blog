'''
Created on Feb 28, 2012

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for service implementations.
'''

from ally.type_legacy import Iterable
import re
from ally.api.type import typeFor
from ally.api.operator.type import TypeQuery, TypeModel
from inspect import isclass
from ally.api.operator.container import Model
from ally.api.criteria import AsBoolean, AsLike, AsEqual, AsOrdered
from itertools import chain

# --------------------------------------------------------------------

def trimIter(iter, size, offset=None, limit=None):
    '''
    Trims the provided iterator based on the offset and limit.
    
    @param iter: Iterable
        The iterator to be trimmed.
    @param size: integer
        The size of the iterator.
    @param offset: integer
        The offset to trim from
    @param limit: integer
        The limit to trim to.
    @return: generator
        A generator that will provide the trimmed iterator.
    '''
    assert isinstance(iter, Iterable), 'Invalid iterator %s' % iter
    assert isinstance(size, int), 'Invalid size %s' % size
    if offset is None: offset = 0
    else: assert isinstance(offset, int), 'Invalid offset %s' % offset
    if limit is None: limit = size
    else: assert isinstance(limit, int), 'Invalid limit %s' % limit
    for _k in zip(range(0, offset), iter): pass
    return (v for v, _k in zip(iter, range(0, limit)))

def processQuery(objects, query, clazz):
    '''
    Filters the iterable of entities based on the provided query.
    
    @param objects: Iterable(model object of clazz)
        The entities objects iterator to be processed.
    @param query: query
        The query object to provide filtering on.
    @param clazz: class
        The model class to use the query on.
    @return: list[model object of clazz]
        The list of processed entities.
    '''
    assert isinstance(objects, Iterable), 'Invalid entities objects iterable %s' % objects
    assert query is not None, 'A query object is required'
    qclazz = query.__class__
    queryType = typeFor(qclazz)
    assert isinstance(queryType, TypeQuery), 'Invalid query %s' % query
    assert isclass(clazz), 'Invalid class %s' % clazz
    modelType = typeFor(clazz)
    assert isinstance(modelType, TypeModel), 'Invalid model class %s' % clazz
    model = modelType.container
    assert isinstance(model, Model)

    filtered = list(objects)
    ordered, unordered = [], []
    properties = {prop.lower(): prop for prop in model.properties}
    for criteria in queryType.query.criterias:
        prop = properties.get(criteria.lower())
        if prop is not None and getattr(qclazz, criteria) in query:
            crt = getattr(query, criteria)
            if isinstance(crt, AsBoolean):
                assert isinstance(crt, AsBoolean)
                if AsBoolean.value in crt:
                    filtered = [obj for obj in filtered if getattr(obj, prop) == crt.value]
            elif isinstance(crt, AsLike):
                assert isinstance(crt, AsLike)
                if AsLike.like in crt:
                    regex = likeAsRegex(crt.like, crt.caseInsensitive or False)
                    filtered = [obj for obj in filtered if regex.match(getattr(obj, prop))]
            elif isinstance(crt, AsEqual):
                assert isinstance(crt, AsEqual)
                if AsEqual.equal in crt:
                    filtered = [obj for obj in filtered if getattr(obj, prop) == crt.equal]
            if isinstance(crt, AsOrdered):
                assert isinstance(crt, AsOrdered)
                if AsOrdered.ascending in crt:
                    if AsOrdered.priority in crt and crt.priority:
                        ordered.append((prop, crt.ascending, crt.priority))
                    else:
                        unordered.append((prop, crt.ascending, None))

            ordered.sort(key=lambda pack: pack[2])
            for prop, asc, __ in reversed(list(chain(ordered, unordered))):
                filtered.sort(key=lambda obj: getattr(obj, prop), reverse=not asc)

    return filtered

def likeAsRegex(like, caseInsensitive=True):
    '''
    Transform a like pattern (ex: heloo%world) resembling a database form, to an actual regex that can be used to
    compare strings.
    
    @param like: string
        The like pattern to convert to regex.
    @param caseInsensitive: boolean
        Flag indicating that the regex should be case insensitive.
    @return: regex
        The regex pattern to use.
    '''
    assert isinstance(like, str), 'Invalid like %s' % like
    assert isinstance(caseInsensitive, bool), 'Invalid case insensitive %s' % caseInsensitive
    likeRegex = like.split('%')
    likeRegex = '.*'.join(re.escape(n) for n in likeRegex)
    likeRegex += '$'
    if caseInsensitive: likeRegex = re.compile(likeRegex, re.IGNORECASE)
    else: likeRegex = re.compile(likeRegex)
    return likeRegex
