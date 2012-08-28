'''
Created on Apr 27, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the specification classes for the media archive.
'''

import abc
from inspect import isclass
from ally.support.api.util_service import namesForQuery
from ally.api.type import typeFor
from ally.api.operator.type import TypeCriteriaEntry
from superdesk.meta.metadata_superdesk import Base
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from superdesk.media_archive.api.meta_info import QMetaInfo
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.api.meta_data import QMetaData

# --------------------------------------------------------------------

class IMetaDataReferencer(metaclass=abc.ABCMeta):
    '''
    Provides the meta data references handler.
    '''

    @abc.abstractclassmethod
    def populate(self, metaData, scheme, thumbSize=None):
        '''
        Processes the meta data references in respect with the specified thumbnail size. The method will take no action if
        the meta data is not relevant for the handler.

        @param metaData: MetaDataMapped (from the meta package)
            The meta data to have the references processed.
        @param scheme: string
            The scheme protocol to provide the references for.
        @param thumbSize: string|None
            The thumbnail size to process for the reference, None value lets the handler peek the thumbnail size.
        @return: MetaData
            The populated meta data, usually the same meta data.
        '''

# --------------------------------------------------------------------

class IMetaDataHandler(metaclass=abc.ABCMeta):
    '''
    Interface that provides the handling for the meta data's.
    '''

    @abc.abstractclassmethod
    def deploy(self):
        '''
        Deploy the handler, at this moment the handler should create the required meta types and thumbnail specifications.
        '''

    @abc.abstractclassmethod
    def process(self, metaDataId, contentPath):
        '''
        Processes the meta data persistence and type association. The meta data will already be in the database this method
        has to update and associate the meta data in respect with the handler. The method will take no action if the content is
        not relevant for the handler.

        @param metaDataId: int
            The id of meta data for the current uploaded content.
        @param contentPath: string
            The location on local file system where the content can be found.
        @return: boolean
            True if the content has been processed, False otherwise.
        '''

# --------------------------------------------------------------------

class IThumbnailManager(IMetaDataReferencer):
    '''
    Interface that defines the API for handling thumbnails.
    '''

    def processThumbnail(self, thumbnailFormatId, imagePath, metaData=None, size=None):
        '''
        Process a file identified by metaData.
        Return the thumbnail content for the given metaData.

        @param thumbnailFormatId: int
            The thumbnail path format identifier
        @param imagePath: str
            The path to the original image from which to generate the thumbnail.
        @param metaData: Metadata
            The object containing the content metadata for which the thumbnail is generated.
        @param size: str
            The size identifier (None for default)
        '''
    
    # --------------------------------------------------------------------
    
    @abc.abstractclassmethod
    def timestampThumbnail(self, thumbnailFormatId, metaData=None, size=None):
        '''
        Provides the thumbnail last modification time stamp.

        @param thumbnailFormatId: integer
            The thumbnail format id to process the timestamp for.
        @param metaData: Metadata
            The object containing the content metadata for which the thumbnail was generated.
        @param size: str
            The thumbnail size (None for default)
        @return: datetime|None
            The datetime of the last modification or None if there is no resource for the thumbnail path.
        '''

# --------------------------------------------------------------------

class IThumbnailCreator(metaclass=abc.ABCMeta):
    '''
    Specification class that provides the thumbnail creation.
    '''

    @abc.abstractclassmethod
    def createThumbnail(self, contentPath, width, height):
        '''
        Create a thumbnail for the provided content.

        @param contentPath: string
            The content local file system path where the original content can be found.
        @param width: integer
            The thumbnail width.
        @param height: integer
            The thumbnail height.
        @return: file bytes object
            The file like object that is the thumbnail.
        '''

# --------------------------------------------------------------------

class QueryIndexer:
    '''
        Manages the query related information about plugins in order to be able to support
        the multi-plugin queries 
    '''
    
    def __init__(self):
        '''
        @ivar metaInfos: set(EntryMetaInfo class)
        The set of plugin specific entry meta info for registered plugins
        @ivar metaDatas: set(EntryMetaData class)
        The set of plugin specific entry meta data for registered plugins    
        
        @ivar metaInfoByCriteria: dict{CriteriaName : set(EntryMetaInfo class)}
        The set of plugin specific entry meta info for registered plugins grouped by criteria name   
        @ivar metaDataByCriteria: dict{CriteriaName : set(EntryMetaData class)}
        The set of plugin specific entry meta data for registered plugins grouped by criteria name   
        
        @ivar infoCriterias: dict{CriteriaName, Criteria class)
        Contains all meta info related criteria names and associated criteria class
        @ivar dataCriterias: dict{CriteriaName, Criteria class)
        Contains all meta data related criteria names and associated criteria class 
        
        '''
        self.metaInfos = set()
        self.metaDatas = set()
        
        self.metaInfoByCriteria = dict()
        self.metaDataByCriteria = dict()
        
        self.infoCriterias = dict()
        self.dataCriterias = dict()
        
    # --------------------------------------------------------------------
        
    def register(self, EntryMetaInfoClass, QMetaInfoClass, EntryMetaDataClass, QMetaDataClass):
        '''
        Construct the meta info base service for the provided classes.
        
        @param EntryMetaInfoClass: class
            A class that contains the specific for media meta info related columns.
        @param QMetaInfoClass: class
            A class that extends QMetaInfo API class.
        @param MetaDataClass: class
            A class that contains the specific for media meta data related columns.
        @param QMetaDataClass: class
            A class that extends QMetaData API class.
        '''
        
        assert isclass(EntryMetaInfoClass) and issubclass(EntryMetaInfoClass, Base), \
        'Invalid entry meta info class %s' % EntryMetaInfoClass
        assert not issubclass(EntryMetaInfoClass, MetaInfoMapped), \
        'The Entry class should be registered, not extended class %s' % EntryMetaInfoClass
        
        assert isclass(QMetaInfoClass) and issubclass(QMetaInfoClass, QMetaInfo), \
        'Invalid meta info query class %s' % QMetaInfoClass
        
        assert isclass(EntryMetaDataClass) and issubclass(EntryMetaDataClass, Base), \
        'Invalid entry meta data class %s' % EntryMetaDataClass
        assert not issubclass(EntryMetaDataClass, MetaDataMapped), \
        'The Entry class should be registered, not extended class %s' % EntryMetaInfoClass
        
        assert isclass(QMetaDataClass) and issubclass(QMetaDataClass, QMetaData), \
        'Invalid meta data query class %s' % QMetaDataClass
            
            
        if (EntryMetaInfoClass in self.metaInfos):
            raise Exception('Already registered the meta info class %s' % EntryMetaInfoClass)    
        
        if (EntryMetaDataClass in self.metaDatas):
            raise Exception('Already registered the meta data class %s' % EntryMetaInfoClass)          
            
            
        for criteria in namesForQuery(QMetaInfoClass):
            criteriaClass = self.infoCriterias.get(criteria)
            if (criteriaClass is None): continue
            
            criteriaType = typeFor(getattr(QMetaInfoClass, criteria)) 
            assert isinstance(criteriaType, TypeCriteriaEntry)
            
            if (criteriaType.forClass != criteriaClass):
                raise Exception("Can't register meta data %s because the %s criteria has type %s " \
                                "and this criteria already exist with a different type %s" % \
                                (EntryMetaInfoClass, criteria, criteriaType.forClass, criteriaClass)) 
       
       
        for criteria in namesForQuery(QMetaDataClass):
            criteriaClass = self.dataCriterias.get(criteria)
            if (criteriaClass is None): continue
            
            criteriaType = typeFor(getattr(QMetaDataClass, criteria)) 
            assert isinstance(criteriaType, TypeCriteriaEntry)
            
            if (criteriaType.forClass != criteriaClass):
                raise Exception("Can't register meta data %s because the %s criteria has type %s " \
                                "and this criteria already exist with a different type %s" % \
                                (EntryMetaDataClass, criteria, criteriaType.forClass, criteriaClass)) 
        
        
        self.metaInfos.add(EntryMetaInfoClass)
        self.metaDatas.add(EntryMetaDataClass)
        
        for criteria in namesForQuery(QMetaInfoClass):
            criteriaType = typeFor(getattr(QMetaInfoClass, criteria))
            assert isinstance(criteriaType, TypeCriteriaEntry)
            
            infoSet = self.metaInfoByCriteria.get(criteria)
            if infoSet is None:
                infoSet = self.metaInfoByCriteria[criteria] = set()
                self.infoCriterias[criteria] = criteriaType.forClass
                          
            infoSet.add(EntryMetaInfoClass)     
            
         
        for criteria in namesForQuery(QMetaDataClass):
            criteriaType = typeFor(getattr(QMetaDataClass, criteria))
            assert isinstance(criteriaType, TypeCriteriaEntry)
            
            dataSet = self.metaDataByCriteria.get(criteria)
            if dataSet is None:
                dataSet = self.metaDataByCriteria[criteria] = set()
                self.dataCriterias[criteria] = criteriaType.forClass
                     
            dataSet.add(EntryMetaDataClass)