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
from ally.core.spec.server import Processors
from ally.container._impl.ioc_setup import ConfigError

# --------------------------------------------------------------------

@ioc.config
def server_pattern_content():
    ''' The pattern used for matching the rest content paths in HTTP URL's'''
    return '^content(/|$)'

@ioc.config
def server_uri():
    ''' The HTTP server name '''
    return 'http://localhost:80/content/'

@ioc.config
def repository_path():
    ''' The repository relative path inside the server document root directory '''
    return None

# --------------------------------------------------------------------
# Creating the content delivery managers

@ioc.entity
def delivery() -> IDelivery:
    if not repository_path():
        raise ConfigError('Missing repository path configuration')
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
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
    h.repositoryPath = repository_path()
    return h

# ---------------------------------

@ioc.entity
def contentHandlers():
    return [localContentHandler()]

@ioc.before(pathProcessors)
def updatePathProcessors():
    if repository_path():
        pathProcessors().append((re.compile(server_pattern_content()), Processors(*contentHandlers())))
