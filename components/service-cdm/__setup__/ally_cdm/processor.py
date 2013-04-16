'''
Created on Jan 5, 2012

@package: service CDM
@copyright: 2012 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl - 3.0.txt
@author: Mugur Rus

Provides the configurations for delivering files from the local file system.
'''

from ..ally_http.processor import contentLengthEncode, allowEncode, \
    internalError, contentTypeResponseEncode
from __setup__.ally_http.processor import headerEncodeResponse
from ally.container import ioc
from ally.core.cdm.processor.content_delivery import ContentDeliveryHandler
from ally.design.processor.assembly import Assembly
from ally.design.processor.handler import Handler
from os import path

# --------------------------------------------------------------------

@ioc.config
def repository_path():
    ''' The repository absolute or relative (to the distribution folder) path from where to serve the files '''
    return path.join('workspace', 'shared', 'cdm')

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.entity
def contentDelivery() -> Handler:
    b = ContentDeliveryHandler()
    b.repositoryPath = repository_path()
    return b

# --------------------------------------------------------------------

@ioc.entity
def assemblyContent() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a content file request.
    '''
    return Assembly('CDM')

# --------------------------------------------------------------------

@ioc.before(assemblyContent)
def updateAssemblyContent():
    assemblyContent().add(internalError(), headerEncodeResponse(), contentDelivery(), allowEncode(), contentTypeResponseEncode(),
                          contentLengthEncode())
    
