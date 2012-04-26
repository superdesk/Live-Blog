'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta data API. 
'''

from ..api.meta_data import IMetaDataService, QMetaData
from ..meta.meta_data import MetaDataMapped
from ally.container.ioc import injected
from ally.exception import InputError, Ref
from inspect import isclass
from sql_alchemy.impl.entity import EntitySupportAlchemy
import abc
from ally.container import wire

# --------------------------------------------------------------------

class IMetaDataReferenceHandler(metaclass=abc.ABCMeta):
    '''
    Interface that provides the references for the meta data's.
    '''

    @abc.abstractclassmethod
    def process(self, metaData, scheme, thumbSize):
        '''
        Processes the meta data references in respect with the specified thumbnail size. If the meta data is not suited or
        the content is not available it has to set the IsAvailable flag to False otherwise if the references have been
        successfully handled it has to set the IsAvailable to True.
        
        @param metaData: MetaDataDB (from the meta package)
            The meta data to have the references processed.
        @param scheme: string
            The scheme protocol to provide the references for.
        @param thumbSize: string|None
            The thumbnail size to process for the reference, None value lets the handler peek the thumbnail size.
        @return: MetaData
            The same data or if is the case another meta data with the references populated.
        '''

# --------------------------------------------------------------------

class MetaDataServiceBaseAlchemy(EntitySupportAlchemy):
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
        assert isclass(MetaDataClass) and issubclass(MetaDataClass, MetaDataMapped), \
        'Invalid meta data class %s' % MetaDataClass
        assert isclass(QMetaDataClass) and issubclass(QMetaDataClass, QMetaData), \
        'Invalid meta data query class %s' % QMetaDataClass
        EntitySupportAlchemy.__init__(self, MetaDataClass, QMetaDataClass)
        self.MetaData = MetaDataClass

    def getById(self, id, scheme, thumbSize=None):
        '''
        @see: IMetaDataService.getById
        '''
        metaData = self.session().query(self.MetaData).get(id)
        if not metaData: raise InputError(Ref(_('Unknown meta data id'), ref=self.MetaData.Id))
        return self._process(metaData, scheme, thumbSize)

    def getMetaDatasCount(self, typeId=None, q=None):
        '''
        @see: IMetaDataService.getMetaDatasCount
        '''
        if typeId:
            return self._getCount(self.MetaData.typeId == typeId, q)
        return self._getCount(query=q)

    def getMetaDatas(self, scheme, typeId=None, offset=None, limit=None, q=None, thumbSize=None):
        '''
        @see: IMetaDataService.getMetaDatas
        '''
        if typeId:
            return self._getAll(self.MetaData.typeId == typeId, q, offset, limit)
        a = self._getAll(query=q, offset=offset, limit=limit)
        print(a)
        return (self._process(metaData, scheme, thumbSize)
                for metaData in self._getAll(query=q, offset=offset, limit=limit))

    # ----------------------------------------------------------------

    def _process(self, metaData, scheme, thumbSize):
        '''
        Internally process the meta data references, method like @see: IMetaDataReferenceHandler.process
        '''
        assert isinstance(metaData, MetaDataMapped), 'Invalid meta data %s' % metaData
        metaData.IsAvailable = False

# --------------------------------------------------------------------

class MetaDataReferenceHandlers(list):
    '''
    The references handlers list used by the meta data in order to get the references.
    '''

@injected
class MetaDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataService):
    '''
    @see: IMetaDataService
    '''

    referenceHandlers = MetaDataReferenceHandlers; wire.entity('referenceHandlers')

    def __init__(self):
        '''
        Construct the meta data service.
        '''
        assert isinstance(self.referenceHandlers, MetaDataReferenceHandlers), \
        'Invalid reference handlers %s' % self.referenceHandlers
        MetaDataServiceBaseAlchemy.__init__(self, MetaDataMapped, QMetaData)

    # ----------------------------------------------------------------

    def _process(self, metaData, scheme, thumbSize):
        '''
        @see: MetaDataServiceBaseAlchemy._process
        '''
        for handler in self.referenceHandlers:
            assert isinstance(handler, IMetaDataReferenceHandler)
            m = handler.process(metaData, scheme, thumbSize)
            assert isinstance(m, MetaDataMapped)
            if m.IsAvailable: return m
        metaData.IsAvailable = False
        return metaData
