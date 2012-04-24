'''
Created on Jun 10, 2011

@package: Newscoop
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
    caseSensitive = bool

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

@criteria
class AsDate:
    '''
    Provides query for properties that can be managed as date.
    '''
    start = Date
    end = Date

@criteria
class AsDateOrdered(AsDate, AsOrdered):
    '''
    Provides the date search and also the ordering.
    '''

# --------------------------------------------------------------------

@criteria
class AsTime:
    '''
    Provides query for properties that can be managed as time.
    '''
    start = Time
    end = Time

@criteria
class AsTimeOrdered(AsTime, AsOrdered):
    '''
    Provides the time search and also the ordering.
    '''

# --------------------------------------------------------------------

@criteria
class AsDateTime:
    '''
    Provides query for properties that can be managed as date time.
    '''
    start = DateTime
    end = DateTime

@criteria
class AsDateTimeOrdered(AsDateTime, AsOrdered):
    '''
    Provides the date time search and also the ordering.
    '''
