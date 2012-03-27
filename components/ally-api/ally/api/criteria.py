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
class AsLike(AsOrdered):
    '''
    Provides query for properties that can be managed by a like function, this will only handle string types
    '''
    like = str
    caseInsensitive = bool

# --------------------------------------------------------------------

@criteria(main='equal')
class AsEqual(AsOrdered):
    '''
    Provides query for properties that can be managed by a equal function, this will only handle string types.
    '''
    equal = str

# --------------------------------------------------------------------

@criteria(main='value')
class AsBoolean(AsOrdered):
    '''
    Provides query for properties that can be managed as booleans.
    '''
    value = bool

# --------------------------------------------------------------------

@criteria
class AsDate(AsOrdered):
    '''
    Provides query for properties that can be managed as date.
    '''
    start = Date
    end = Date

@criteria
class AsTime(AsOrdered):
    '''
    Provides query for properties that can be managed as time.
    '''
    start = Time
    end = Time

@criteria
class AsDateTime(AsOrdered):
    '''
    Provides query for properties that can be managed as date time.
    '''
    start = DateTime
    end = DateTime
