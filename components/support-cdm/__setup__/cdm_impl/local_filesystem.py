'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides the configurations for the CDM local filesystem implementation.
'''

from cdm.impl.local_filesystem import *
from ally.container import ioc

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
    cdm.repositoryPath = d.getRepositoryPath()
    return cdm

# ---------------------------------

@ioc.entity
def cdms():
    return [localFileSystemCDM()]
