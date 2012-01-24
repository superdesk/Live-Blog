'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides the configurations for the CDM local filesystem implementation.
'''

from cdm.impl.local_filesystem import IDelivery, LocalFileSystemCDM, HTTPDelivery
from ally.container import ioc
from cdm.spec import ICDM
from __setup__.ally_core_http.processor import pathProcessors
import re
from ally.core.cdm.processor.content_delivery import ContentDeliveryHandler
from __setup__.ally_core_http import server_port
from ally.core.spec.server import Processors
from ally.container._impl.ioc_setup import ConfigError

# --------------------------------------------------------------------

@ioc.config
def server_pattern_content():
    ''' The pattern used for matching the rest content paths in HTTP URL's'''
    return '^content(/|$)'

@ioc.config
def server_name():
    ''' The HTTP server name '''
    return 'localhost'

@ioc.config
def server_document_root():
    ''' The HTTP server document root directory '''
    return None

@ioc.config
def repository_subdirectory():
    ''' The repository relative path inside the server document root directory '''
    return 'repository'

# --------------------------------------------------------------------
# Creating the content delivery managers

@ioc.entity
def delivery() -> IDelivery:
    if not server_document_root(): raise ConfigError('No server document root configuration')
    d = HTTPDelivery()
    d.serverName = server_name()
    d.port = server_port()
    d.documentRoot = server_document_root()
    d.repositorySubdir = repository_subdirectory()
    return d

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM();
    cdm.delivery = delivery()
    return cdm

@ioc.entity
def cdms():
    return [contentDeliveryManager()]

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.entity
def localContentHandler():
    h = ContentDeliveryHandler()
    h.documentRoot = server_document_root()
    h.repositorySubdir = repository_subdirectory()
    return h

# ---------------------------------

@ioc.entity
def contentHandlers():
    return [localContentHandler()]

@ioc.before(pathProcessors)
def updatePathProcessors():
    if server_document_root():
        pathProcessors().append((re.compile(server_pattern_content()), Processors(*contentHandlers())))
