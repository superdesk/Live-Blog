'''
Created on Apr 27, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the specification classes for the media archive.
'''

from ally.api.operator.type import TypeCriteriaEntry
from ally.api.type import typeFor
from ally.support.api.util_service import namesForQuery
from inspect import isclass
from superdesk.media_archive.api.meta_data import QMetaData
from superdesk.media_archive.api.meta_info import QMetaInfo
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from superdesk.meta.metadata_superdesk import Base
import abc

# --------------------------------------------------------------------

class IMetaDataReferencer(metaclass=abc.ABCMeta):
    '''
    Provides the meta data references handler.
    '''

    @abc.abstractclassmethod
    def populate(self, metaData, scheme, size=None):
        '''
        Processes the meta data references in respect with the specified thumbnail size. The method will take no action if
        the meta data is not relevant for the handler.

        @param metaData: MetaDataMapped (from the meta package)
            The meta data to have the references processed.
        @param scheme: string
            The scheme protocol to provide the references for.
        @param size: string|None
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
    def processByInfo(self, metaDataMapped, contentPath, contentType):
        '''
        Processes the meta data persistence and type association. The meta data will already be in the database this method
        has to update and associate the meta data in respect with the handler. By using the contentType and file extension
        info, the plugin will decide if process or not the request. The method will take no action if fails to process the
        content (content has wrong format, or wrong declared format).

        @param metaDataMapped: MetaDataMapped
            The meta data mapped for the current uploaded content.
        @param contentPath: string
            The path were the media file is stored
        @param contentType: string
            The content type of uploaded file.
        @return: boolean
            True if the content has been processed, False otherwise.
        '''

    @abc.abstractclassmethod
    def process(self, metaDataMapped, contentPath):
        '''
        Processes the meta data persistence and type association. The meta data will already be in the database this method
        has to update and associate the meta data and meta info in respect with the handler. The method will take no action if fails to process the
        content (content has wrong format)

        @param metaDataMapped: MetaDataMapped
            The meta data mapped for the current uploaded content.
        @contentPath: string
            The path were the media file is stored
        @return: boolean
            True if the content has been processed, False otherwise.
        '''

    @abc.abstractclassmethod
    def addMetaInfo(self, metaDataMapped):
        '''
        Add an empty meta info for the current plugin

        @param metaDataMapped: MetaDataMapped
            The meta data mapped for the current uploaded content.
        @return: MetaInfo
            Return the MetaInfoMapped created object.
        '''

# --------------------------------------------------------------------

class IThumbnailManager(IMetaDataReferencer):
    '''
    Interface that defines the API for handling thumbnails.
    '''

    @abc.abstractclassmethod
    def putThumbnail(self, thumbnailFormatId, imagePath, metaData=None):
        '''
        Places a thumbnail identified by thumbnail format id.

        @param thumbnailFormatId: integer
            The thumbnail path format identifier
        @param imagePath: string
            The path to the original image from which to generate the thumbnail.
        @param metaData: MetaData|None
            The object containing the content metadata for which the thumbnail is placed.
        '''
        
    @abc.abstractclassmethod  
    def deleteThumbnail(self, thumbnailFormatId, metaData): 
        '''
        Deletes all thumbnails associated to the current MetaData

        @param thumbnailFormatId: integer
            The thumbnail path format identifier
        @param metaData: MetaData
            The MetaData associated to thumbnails
        '''  

class IThumbnailProcessor(metaclass=abc.ABCMeta):
    '''
    Specification class that provides the thumbnail processing.
    '''

    @abc.abstractclassmethod
    def processThumbnail(self, source, destination, width=None, height=None):
        '''
        Create a thumbnail for the provided content, if the width or height is not provided then no resizing will occur.

        @param source: string
            The content local file system path where the thumbnail to be resized can be found.
         @param destination: string
            The destination local file system path where to place the resized thumbnail.
        @param width: integer|None
            The thumbnail width.
        @param height: integer|None
            The thumbnail height.
        '''

class IQueryIndexer:
    '''
        Manages the query related information about plugins in order to be able to support
        the multi-plugin queries
    '''

    def __init__(self):
        '''
        '''

    # --------------------------------------------------------------------

    def register(self, EntryMetaInfoClass, QMetaInfoClass, EntryMetaDataClass, QMetaDataClass, type):
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
        @param typeId: int
            The id of the type associated to the current registered plugin
        '''

# --------------------------------------------------------------------

class QueryIndexer(IQueryIndexer):
    '''
        Manages the query related information about plugins in order to be able to support
        the multi-plugin queries
    '''

    def __init__(self):
        '''
        @ivar metaDatasByInfo: dict{MetaInfoName: MetaData class}
        Contains all MetaData class associated to MetaInfoName
        @ivar metaInfosBydata: dict{MetaDataName: MetaInfo class}
        Contains all MetaInfo class associated to MetaDataName

        @ivar typeByMetaData: dict{MetaDataName: typeId}
        Contains all MetaData Names and the associated type
        @ivar typeByMetaInfo: dict{MetaInfoName: typeId}
        Contains all MetaInfo Names and the associated type

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

        self.metaDatasByInfo = dict()
        self.metaInfosByData = dict()

        self.queryByInfo = dict()
        self.queryByData = dict()

        self.typesByMetaData = dict()
        self.typesByMetaInfo = dict()

        self.metaInfos = set()
        self.metaDatas = set()

        self.metaInfoByCriteria = dict()
        self.metaDataByCriteria = dict()

        self.infoCriterias = dict()
        self.dataCriterias = dict()

    # --------------------------------------------------------------------

    def register(self, EntryMetaInfoClass, QMetaInfoClass, EntryMetaDataClass, QMetaDataClass, type):
        '''
        see: IQueryIndexer.register()
        '''

        assert isclass(EntryMetaInfoClass) and issubclass(EntryMetaInfoClass, Base), \
        'Invalid entry meta info class %s' % EntryMetaInfoClass

        assert isclass(EntryMetaInfoClass) and EntryMetaInfoClass is MetaInfoMapped or \
        not issubclass(EntryMetaInfoClass, MetaInfoMapped), \
        'The Entry class should be registered, not extended class %s' % EntryMetaInfoClass

        assert isclass(QMetaInfoClass) and issubclass(QMetaInfoClass, QMetaInfo), \
        'Invalid meta info query class %s' % QMetaInfoClass

        assert isclass(EntryMetaDataClass) and issubclass(EntryMetaDataClass, Base), \
        'Invalid entry meta data class %s' % EntryMetaDataClass

        assert isclass(EntryMetaDataClass) and EntryMetaDataClass is MetaDataMapped or \
        not issubclass(EntryMetaDataClass, MetaDataMapped), \
        'The Entry class should be registered, not extended class %s' % EntryMetaInfoClass

        assert isclass(QMetaDataClass) and issubclass(QMetaDataClass, QMetaData), \
        'Invalid meta data query class %s' % QMetaDataClass


        if (EntryMetaInfoClass in self.metaInfos):
            raise Exception('Already registered the meta info class %s' % EntryMetaInfoClass)

        if (EntryMetaDataClass in self.metaDatas):
            raise Exception('Already registered the meta data class %s' % EntryMetaInfoClass)


        self.metaDatasByInfo[EntryMetaInfoClass.__name__] = EntryMetaDataClass
        self.metaInfosByData[EntryMetaDataClass.__name__] = EntryMetaInfoClass

        self.typesByMetaData[EntryMetaDataClass.__name__] = type
        self.typesByMetaInfo[EntryMetaInfoClass.__name__] = type

        self.queryByData[EntryMetaDataClass.__name__] = QMetaDataClass
        self.queryByInfo[EntryMetaInfoClass.__name__] = QMetaInfoClass


        for criteria in namesForQuery(QMetaInfoClass):
            criteriaClass = self.infoCriterias.get(criteria)
            if (criteriaClass is None): continue

            criteriaType = typeFor(getattr(QMetaInfoClass, criteria))
            assert isinstance(criteriaType, TypeCriteriaEntry)

            if (criteriaType.clazz != criteriaClass):
                raise Exception("Can't register meta data %s because the %s criteria has type %s " \
                                "and this criteria already exist with a different type %s" % \
                                (EntryMetaInfoClass, criteria, criteriaType.clazz, criteriaClass))


        for criteria in namesForQuery(QMetaDataClass):
            criteriaClass = self.dataCriterias.get(criteria)
            if (criteriaClass is None): continue

            criteriaType = typeFor(getattr(QMetaDataClass, criteria))
            assert isinstance(criteriaType, TypeCriteriaEntry)

            if (criteriaType.clazz != criteriaClass):
                raise Exception("Can't register meta data %s because the %s criteria has type %s " \
                                "and this criteria already exist with a different type %s" % \
                                (EntryMetaDataClass, criteria, criteriaType.clazz, criteriaClass))


        self.metaInfos.add(EntryMetaInfoClass)
        self.metaDatas.add(EntryMetaDataClass)

        for criteria in namesForQuery(QMetaInfoClass):
            criteriaType = typeFor(getattr(QMetaInfoClass, criteria))
            assert isinstance(criteriaType, TypeCriteriaEntry)

            infoSet = self.metaInfoByCriteria.get(criteria)
            if infoSet is None:
                infoSet = self.metaInfoByCriteria[criteria] = set()
                self.infoCriterias[criteria] = criteriaType.clazz

            infoSet.add(EntryMetaInfoClass)


        for criteria in namesForQuery(QMetaDataClass):
            criteriaType = typeFor(getattr(QMetaDataClass, criteria))
            assert isinstance(criteriaType, TypeCriteriaEntry)

            dataSet = self.metaDataByCriteria.get(criteria)
            if dataSet is None:
                dataSet = self.metaDataByCriteria[criteria] = set()
                self.dataCriterias[criteria] = criteriaType.clazz

            dataSet.add(EntryMetaDataClass)
