'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta info API. 
'''

from ..api.meta_data import QMetaData
from ..api.meta_info import IMetaInfoService, QMetaInfo
from ..meta.meta_data import MetaDataMapped
from ..meta.meta_info import MetaInfo
from ally.container.ioc import injected
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from sql_alchemy.impl.entity import EntityGetServiceAlchemy
from inspect import isclass

# --------------------------------------------------------------------

class MetaInfoServiceBaseAlchemy(EntityGetServiceAlchemy):
    '''
    Base SQL alchemy implementation for meta info type services.
    '''

    def __init__(self, MetaInfoClass, QMetaInfoClass, MetaDataClass, QMetaDataClass):
        '''
        Construct the meta info base service for the provided classes.
        
        @param MetaInfoClass: class
            A class that extends MetaInfo meta class.
        @param QMetaInfoClass: class
            A class that extends QMetaInfo API class.
        @param MetaDataClass: class
            A class that extends MetaData meta class.
        @param QMetaDataClass: class
            A class that extends QMetaData API class.
        '''
        assert isclass(MetaInfoClass) and issubclass(MetaInfoClass, MetaInfo), \
        'Invalid meta info class %s' % MetaInfoClass
        assert isclass(QMetaInfoClass) and issubclass(QMetaInfoClass, QMetaInfo), \
        'Invalid meta info query class %s' % QMetaInfoClass
        assert isclass(MetaDataClass) and issubclass(MetaDataClass, MetaDataMapped), \
        'Invalid meta data class %s' % MetaDataClass
        assert isclass(QMetaDataClass) and issubclass(QMetaDataClass, QMetaData), \
        'Invalid meta data query class %s' % QMetaDataClass
        EntityGetServiceAlchemy.__init__(self, MetaInfoClass, QMetaInfoClass)
        self.MetaInfo = MetaInfoClass
        self.QMetaInfo = QMetaInfoClass
        self.MetaData = MetaDataClass
        self.QMetaData = QMetaDataClass

    def getMetaInfosCount(self, dataId=None, languageId=None, qi=None, qd=None):
        '''
        @see: IMetaInfoService.getMetaInfosCount
        '''
        return self._buildSql(dataId, languageId, qi, qd).count()

    def getMetaInfos(self, dataId=None, languageId=None, offset=None, limit=10, qi=None, qd=None):
        '''
        @see: IMetaInfoService.getMetaInfos
        '''
        sql = self._buildSql(dataId, languageId, qi, qd)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    # ----------------------------------------------------------------

    def _buildSql(self, dataId, languageId, qi, qd):
        '''
        Build the sql alchemy based on the provided data.
        '''
        sql = self.session().query(self.MetaInfo)
        if dataId: sql = sql.filter(self.MetaInfo.MetaData == dataId)
        if languageId: sql = sql.filter(self.MetaInfo.Language == languageId)
        if qi:
            assert isinstance(qi, self.QMetaInfo), 'Invalid meta info query %s' % qi
            sql = buildQuery(sql, qi, self.MetaInfo)
        if qd:
            assert isinstance(qd, self.QMetaData), 'Invalid meta data query %s' % qd
            sql = buildQuery(sql.join(self.MetaData), qd, self.MetaData)
        return sql

# --------------------------------------------------------------------

@injected
class MetaInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IMetaInfoService):
    '''
    @see: IMetaInfoService
    '''

    def __init__(self):
        '''
        Construct the meta info service.
        '''
        MetaInfoServiceBaseAlchemy.__init__(self, MetaInfo, QMetaInfo, MetaDataMapped, QMetaData)
