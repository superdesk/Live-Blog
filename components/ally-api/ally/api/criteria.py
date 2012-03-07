'''
Created on Jun 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides general used criteria for APIs.
'''

from . import configure
from .type import Date, Time, DateTime
from ally.api.config import criteria

# --------------------------------------------------------------------

@criteria
class AsOrdered:
    '''
    Provides query for properties that can be ordered.
    '''
    orderAscending = bool
    
    def __init__(self):
        self._index = None
    
    def orderAsc(self):
        self.orderAscending = True
        
    def orderDesc(self):
        self.orderAscending = False
        
    def index(self):
        '''
        The index is the position of the ordered in the orders. Basically if you require to know in which order
        the ordering have been provided the index provides that.
        
        @return: integer|None
            The position in the query instance at which this order is considered, the indexes are not required to be
            consecutive in a query. None if there is no ordering set for this criteria.
        '''
        return self._index

def _orderAscendingOnSet(self):
    '''
    Listener method used in determining the index.
    '''
    if self._index is None:
        self._index = getattr(self.query, '_index', 1)
        setattr(self.query, '_index', self._index + 1)

def _orderAscendingOnDel(self):
    '''
    Listener method used in determining the index.
    '''
    self._index = None
    
AsOrdered.orderAscendingOnSet = _orderAscendingOnSet
AsOrdered.orderAscendingOnDel = _orderAscendingOnDel

# --------------------------------------------------------------------

# register as a default condition for descriptors the like
configure.DEFAULT_CONDITIONS.append('like')

@criteria
class AsLike(AsOrdered):
    '''
    Provides query for properties that can be managed by a like function, this will only handle string types
    '''
    like = str
    caseInsensitive = bool

# --------------------------------------------------------------------

# register as a default condition for descriptors the equal
configure.DEFAULT_CONDITIONS.append('equal')

@criteria
class AsEqual(AsOrdered):
    '''
    Provides query for properties that can be managed by a equal function, this will only handle string types.
    '''
    equal = str

# --------------------------------------------------------------------

# register as a default condition for descriptors the flag
configure.DEFAULT_CONDITIONS.append('flag')

@criteria
class AsBoolean(AsOrdered):
    '''
    Provides query for properties that can be managed as booleans.
    '''
    flag = bool

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
