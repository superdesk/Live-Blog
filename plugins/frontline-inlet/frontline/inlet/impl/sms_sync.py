'''
Created on Oct 22, 2013

@package: frontline-inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API implementation for SMS sync.
'''

from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from ally.api.extension import IterPart
from ally.container import wire
from frontline.inlet.api.sms_sync import ISmsSyncService, QSmsSync
from frontline.inlet.meta.sms_sync import SmsSyncMapped

# --------------------------------------------------------------------

@setup(ISmsSyncService, name='SmsSyncService')
class SmsSyncServiceAlchemy(EntityServiceAlchemy, ISmsSyncService):
    '''
    Implementation for @see ISmsSyncService
    '''
    sms_provider_type = 'smsfeed'; wire.config('sms_provider_type', doc='''
    Key of the source type for SMS providers''')

    def __init__(self):
        '''
        Construct the Sms sync service.
        '''
        EntityServiceAlchemy.__init__(self, SmsSyncMapped, QSmsSync)

    def getAll(self, offset=None, limit=None, detailed=False, q=None):
        '''
        @see ISmsSyncService.getAll
        '''
        sql = self.session().query(SmsSyncMapped)
        if q:
            assert isinstance(q, QSmsSync), 'Invalid Sms sync query %s' % q
            sql = buildQuery(sql, q, SmsSyncMapped)

        sql = sql.join(SourceMapped, SourceMapped.Id == SmsSyncMapped.Source)

        sql_prov = self.session().query(SourceMapped.URI)
        sql_prov = sql_prov.join(SourceTypeMapped, SourceTypeMapped.id == SourceMapped.typeId)
        sql_prov = sql_prov.filter(SourceTypeMapped.Key == self.sms_provider_type)

        sql = sql.filter(SourceMapped.OriginURI.in_(sql_prov))

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()
        
        
    def getSmsSyncByBlogAndSource(self, Blog, source):
        '''
        @see ISmsSyncService.getSmsSyncBySmsAndSource
        '''
        try:
            sql = self.session().query(SmsSyncMapped)
            sql = sql.filter(SmsSyncMapped.Blog == Blog)
            sql = sql.filter(SmsSyncMapped.Source ==source)
            return sql.one()
        except: return None


