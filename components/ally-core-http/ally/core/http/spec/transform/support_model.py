'''
Created on Jul 27, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support model encode implementations. 
'''

from ally.core.spec.resources import Path
from ally.design.bean import Attribute, Bean
from collections import OrderedDict, Callable
import abc

# --------------------------------------------------------------------

NO_MODEL_PATH = 1 << 1
# Flag indicating that no model path should be rendered.

class DataModel(Bean):
    '''
    Contains data used for additional support in encoding the model. The data model is used by the encode model to alter
    the encoding depending on path elements and filters.
    '''
    flag = int; flag = Attribute(flag, default=0, doc='''
    @rtype: integer
    Flag indicating several situations for the data encode.
    ''')
    modelPaths = dict; modelPaths = Attribute(modelPaths, factory=dict, doc='''
    @rtype: dictionary{ModelType:Path}
    The model paths that are directly linked with the encoded model. When a model instance is processed
    this model paths will get updated with the encoded model information. The key represents the model type
    that the path needs to be updated with and the value the path to be updated.
    ''')
    path = Path; path = Attribute(path, doc='''
    @rtype: Path|None
    The path of the model.
    ''')
    accessiblePath = Path; accessiblePath = Attribute(accessiblePath, doc='''
    @rtype: Path|None
    The path for the accessible paths.
    ''')
    accessibleIsProcessed = bool; accessibleIsProcessed = Attribute(accessibleIsProcessed, default=False, doc='''
    @rtype: boolean
    Flag indicating that the accessible dictionary has been processed.
    ''')
    accessible = dict; accessible = Attribute(accessible, factory=OrderedDict, doc='''
    @rtype: dictionary{string, Path}
    The accessible path for the encoded model.
    ''')
    filter = set; filter = Attribute(filter, frozenset, factory=set, doc='''
    @rtype: set(string)
    The properties to be rendered for the model encode, this set needs to include also the accessible paths.
    ''')
    datas = dict; datas = Attribute(datas, factory=dict, doc='''
    @rtype: dictionary{string, DataModel}
    The data models to be used for the properties of the encoded model.
    ''')
    fetchReference = object; fetchReference = Attribute(fetchReference, doc='''
    @rtype: object
    The fetch reference for the fetch encode.
    ''')
    fetchEncode = Callable; fetchEncode = Attribute(fetchEncode, doc='''
    @rtype: Callable
    The fetch encode to be used.
    ''')
    fetchData = object; fetchData = Attribute(fetchData, doc='''
    @rtype: DataModel
    The fetch data model to be used.
    ''')

# --------------------------------------------------------------------

class IFetcher(metaclass=abc.ABCMeta):
    '''
    Specification for model fetching.
    '''
    __slots__ = ()

    @abc.abstractclassmethod
    def fetch(self, reference, valueId):
        '''
        Fetch the model object that is specific for the provided reference.
        
        @param reference: Reference
            The reference of the model object to fetch.
        @param valueId: object
            The value id for the model object to fetch.
        @return: object|None
            The model object corresponding to the reference and value id, None if the object cannot be provided.
        '''
