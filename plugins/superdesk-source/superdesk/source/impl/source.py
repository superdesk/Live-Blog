'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for source API.
'''

from ..api.source import ISourceService, QSource
from ..meta.source import SourceMapped
from ..meta.type import SourceTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from ally.api.criteria import AsLike
from sql_alchemy.support.util_service import iterateCollection, buildQuery
from functools import reduce
from sqlalchemy.sql.expression import or_
from ally.api.validate import validate

# --------------------------------------------------------------------

@injected
@setup(ISourceService, name='sourceService')
@validate(SourceMapped)
class SourceServiceAlchemy(EntityGetCRUDServiceAlchemy, ISourceService):
    '''Implementation for @see: ISourceService'''
    allNames = (SourceMapped.Name, SourceMapped.URI)

    def __init__(self):
        '''Construct the source service.'''
        EntityGetCRUDServiceAlchemy.__init__(self, SourceMapped, QSource, all=self.queryAll)

    def getAll(self, typeKey=None, q=None, **options):
        ''':see: ISourceService.getAll'''
        assert self.QEntity is not None, 'No query available for this service'
        sql = self.session().query(self.MappedId)
        if typeKey:
            sql = sql.join(SourceTypeMapped).filter(SourceTypeMapped.Key == typeKey)
        if q is not None:
            assert isinstance(q, self.QEntity), 'Invalid query %s' % q
            sql = buildQuery(sql, q, self.Mapped, orderBy=self.MappedId, autoJoin=True, **self._mapping)
        return iterateCollection(sql, **options)

    # ----------------------------------------------------------------

    def queryAll(self, sql, crit):
        '''Processes the all query.'''
        assert isinstance(crit, AsLike), 'Invalid criteria %s' % crit
        filters = []
        if AsLike.like in crit:
            for col in self.allNames: filters.append(col.like(crit.like))
        elif AsLike.ilike in crit:
            for col in self.allNames: filters.append(col.ilike(crit.ilike))
        sql = sql.filter(reduce(or_, filters))
        return sql
