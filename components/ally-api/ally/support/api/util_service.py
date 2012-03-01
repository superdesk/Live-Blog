'''
Created on Feb 28, 2012

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for service implementations.
'''

from ally.type_legacy import Iterator
import re

# --------------------------------------------------------------------

def trimIter(iter, size, offset=None, limit=None):
    '''
    Trims the provided iterator based on the offset and limit.
    
    @param iter: Iterator
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
    assert isinstance(iter, Iterator), 'Invalid iterator %s' % iter
    assert isinstance(size, int), 'Invalid size %s' % size
    if offset is None: offset = 0
    else: assert isinstance(offset, int), 'Invalid offset %s' % offset
    if limit is None: limit = size
    else: assert isinstance(limit, int), 'Invalid limit %s' % limit
    for _k in zip(range(0, offset), iter): pass
    return (v for v, _k in zip(iter, range(0, limit)))

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
    likeRegex = '.+'.join(re.escape(n) for n in likeRegex)
    likeRegex += '$'
    if caseInsensitive: likeRegex = re.compile(likeRegex, re.IGNORECASE)
    else: likeRegex = re.compile(likeRegex)
    return likeRegex
