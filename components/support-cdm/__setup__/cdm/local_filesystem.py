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

# --------------------------------------------------------------------

@ioc.config
def server_pattern_content():
    ''' The pattern used for matching the rest content paths in HTTP URL's'''
    return '^content(/|$)'

# --------------------------------------------------------------------
# Creating the content delivery managers

@ioc.entity
def HTTPDelivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverName = 'localhost'
    d.documentRoot = '/var/www'
    d.repositorySubdir = 'repository'
    d.port = 80
    return d

@ioc.entity
def localFileSystemCDM() -> ICDM:
    d = HTTPDelivery()
    cdm = LocalFileSystemCDM();
    cdm.delivery = d
    return cdm

@ioc.entity
def cdms():
    return [localFileSystemCDM()]

# ---------------------------------

@ioc.entity
def contentHandlers():
    return []

#@ioc.before(pathProcessors)
def updatePathProcessors():
    pathProcessors().append((re.compile(server_pattern_content()), contentHandlers()))
