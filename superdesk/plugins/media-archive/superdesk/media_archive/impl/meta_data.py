'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta data API. 
'''

from ..api.meta_data import IMetaDataService, QMetaData
from ..meta.meta_data import MetaData
from ally.container.ioc import injected
from sql_alchemy.impl.entity import EntityGetServiceAlchemy
from inspect import isclass

# --------------------------------------------------------------------

class MetaDataServiceBaseAlchemy(EntityGetServiceAlchemy):
    '''
    Base SQL alchemy implementation for meta data type services.
    '''

    def __init__(self, MetaDataClass, QMetaDataClass):
        '''
        Construct the meta data base service for the provided classes.
        
        @param MetaDataClass: class
            A class that extends MetaData meta class.
        @param QMetaDataClass: class
            A class that extends QMetaData API class.
        '''
        assert isclass(MetaDataClass) and issubclass(MetaDataClass, MetaData), \
        'Invalid meta data class %s' % MetaDataClass
        assert isclass(QMetaDataClass) and issubclass(QMetaDataClass, QMetaData), \
        'Invalid meta data query class %s' % QMetaDataClass
        EntityGetServiceAlchemy.__init__(self, MetaDataClass, QMetaDataClass)
        self.MetaData = MetaDataClass

    def getMetaDatasCount(self, typeId=None, q=None):
        '''
        @see: IMetaDataService.getMetaDatasCount
        '''
        if typeId:
            return self._getCount(self.MetaData.Type == typeId, q)
        return self._getCount(query=q)

    def getMetaDatas(self, typeId=None, offset=None, limit=10, q=None):
        '''
        @see: IMetaDataService.getMetaDatas
        '''
        if typeId:
            return self._getAll(self.MetaData.Type == typeId, q, offset, limit)
        return self._getAll(query=q, offset=offset, limit=limit)

# --------------------------------------------------------------------

@injected
class MetaDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataService):
    '''
    @see: IMetaDataService
    '''

    def __init__(self):
        '''
        Construct the meta data service.
        '''
        MetaDataServiceBaseAlchemy.__init__(self, MetaData, QMetaData)
