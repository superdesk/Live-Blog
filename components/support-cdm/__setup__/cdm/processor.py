'''
Created on Jan 5, 2012

@package: support cdm
@copyright: 2012 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl - 3.0.txt
@author: Mugur Rus

Provides the configurations for delivering files from the local file system.
'''

from ..ally_core.processor import explainError, renderer
from ..ally_core_http.processor import header, internalError, allowEncode, \
    acceptDecode, pathAssemblies
from ally.container import ioc
from ally.core.cdm.processor.content_delivery import ContentDeliveryHandler
from ally.design.processor import Handler, Assembly
from os import path
from __setup__.ally_core_http.processor import contentTypeEncode

# --------------------------------------------------------------------

@ioc.config
def server_provide_content():
    ''' Flag indicating that this server should provide content from the local configured repository path'''
    return True

@ioc.config
def server_pattern_content():
    ''' The pattern used for matching the rest content paths in HTTP URL's'''
    return '^content(/|$)'

@ioc.config
def repository_path():
    ''' The repository absolute or relative (to the distribution folder) path '''
    return path.join('workspace', 'cdm')

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.entity
def assemblyContent() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a content file request.
    '''
    return Assembly()

@ioc.entity
def contentDelivery() -> Handler:
    h = ContentDeliveryHandler()
    h.repositoryPath = repository_path()
    return h

# --------------------------------------------------------------------

@ioc.before(assemblyContent)
def updateAssemblyContent():
    assemblyContent().add(internalError(), contentDelivery(), header(), acceptDecode(), renderer(), explainError(),
                          allowEncode(), contentTypeEncode())

@ioc.before(pathAssemblies)
def updatePathAssembliesForContent():
    if server_provide_content(): pathAssemblies().append((server_pattern_content(), assemblyContent()))
