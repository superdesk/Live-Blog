'''
Created on Aug 28, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for query criteria service.
'''

from .domain_archive import modelArchive
from ally.api.type import Iter
from ally.api.config import query, service, call
from ally.api.criteria import AsLikeOrdered

# --------------------------------------------------------------------

@modelArchive(id='Key')
class QueryCriteria:
    '''Provides the info about the criteria of multi-plugin query.'''
    Key = str
    Criteria = str
    Name = str
    Types = str

    def __init__(self, Key, Criteria, Types, Name=None):
        self.Key = Key
        self.Criteria = Criteria
        self.Types = Types
        self.Name = Name

# --------------------------------------------------------------------

@query(QueryCriteria)
class QQueryCriteria:
    '''The query for query criteria model.'''
    key = AsLikeOrdered
    criteria = AsLikeOrdered
    types = AsLikeOrdered
    name = AsLikeOrdered

# --------------------------------------------------------------------

@service
class IQueryCriteriaService:
    '''Provides the service methods for the query criteria service.'''

    @call
    def getCriterias(self, q:QQueryCriteria=None) -> Iter(QueryCriteria):
        '''Provides the list of query criteria that respect the given query conditions.'''
