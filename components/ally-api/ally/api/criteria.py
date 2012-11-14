'''
Created on Jun 10, 2011

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides general used criteria for APIs.
'''

from .type import Date, Time, DateTime
from ally.api.config import criteria

# --------------------------------------------------------------------

@criteria
class AsOrdered:
    '''
    Provides query for properties that can be ordered.
    '''
    ascending = bool
    priority = int

    def orderAsc(self):
        self.ascending = True

    def orderDesc(self):
        self.ascending = False

# --------------------------------------------------------------------

@criteria(main='like')
class AsLike:
    '''
    Provides query for properties that can be managed by a like function, this will only handle string types
    '''
    like = str
    ilike = str

@criteria
class AsLikeOrdered(AsLike, AsOrdered):
    '''
    Provides the like search and also the ordering.
    '''

# --------------------------------------------------------------------

@criteria(main='equal')
class AsEqual:
    '''
    Provides query for properties that can be managed by a equal function, this will only handle string types.
    '''
    equal = str

@criteria
class AsEqualOrdered(AsEqual, AsOrdered):
    '''
    Provides the equal search and also the ordering.
    '''

# --------------------------------------------------------------------

@criteria(main='value')
class AsBoolean:
    '''
    Provides query for properties that can be managed as booleans.
    '''
    value = bool

@criteria
class AsBooleanOrdered(AsBoolean, AsOrdered):
    '''
    Provides the booleans search and also the ordering.
    '''

# --------------------------------------------------------------------

@criteria(main=('start', 'end'))
class AsRange:
    '''
    Provides a query for properties that need to be handled as a range.
    '''
    start = str
    end = str
    since = str
    until = str

@criteria
class AsRangeOrdered(AsRange, AsOrdered):
    '''
    Provides the equal search and also the ordering.
    '''

# --------------------------------------------------------------------

@criteria(main=('start', 'end'))
class AsDate:
    '''
    Provides query for properties that can be managed as date.
    '''
    start = Date
    end = Date
    since = Date
    until = Date

@criteria
class AsDateOrdered(AsDate, AsOrdered):
    '''
    Provides the date search and also the ordering.
    '''

# --------------------------------------------------------------------

@criteria(main=('start', 'end'))
class AsTime:
    '''
    Provides query for properties that can be managed as time.
    '''
    start = Time
    end = Time
    since = Time
    until = Time

@criteria
class AsTimeOrdered(AsTime, AsOrdered):
    '''
    Provides the time search and also the ordering.
    '''

# --------------------------------------------------------------------

@criteria(main=('start', 'end'))
class AsDateTime:
    '''
    Provides query for properties that can be managed as date time.
    '''
    start = DateTime
    end = DateTime
    since = DateTime
    until = DateTime

@criteria
class AsDateTimeOrdered(AsDateTime, AsOrdered):
    '''
    Provides the date time search and also the ordering.
    '''
