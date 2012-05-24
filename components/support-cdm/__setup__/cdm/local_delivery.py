'''
Created on Jan 5, 2012

@package: support cdm
@copyright: 2012 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl - 3.0.txt
@author: Mugur Rus

Provides the configurations for delivering files from the local file system.
'''

from ..ally_core.processor import explainError
from ..ally_core_http.processor import pathProcessors
from ally.container import ioc
from ally.core.cdm.processor.content_delivery import ContentDeliveryHandler
from ally.core.spec.server import Processors, IProcessor
from os import path
import re

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
def localContentHandler() -> IProcessor:
    h = ContentDeliveryHandler()
    h.repositoryPath = repository_path()
    return h

# ---------------------------------

@ioc.entity
def contentHandlers():
    return [explainError(), localContentHandler()]

@ioc.before(pathProcessors)
def updatePathProcessors():
    if server_provide_content():
        pathProcessors().append((re.compile(server_pattern_content()), Processors(*contentHandlers())))
