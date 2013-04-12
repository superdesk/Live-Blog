'''
Created on Jul 15, 2011

@package: support cdm
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains setup and configuration files for cdm file system.
'''

from ally.cdm.impl.local_filesystem import IDelivery, HTTPDelivery, \
    LocalFileSystemLinkCDM, LocalFileSystemCDM
from ally.cdm.spec import ICDM
from ally.container import ioc
from os import path

# --------------------------------------------------------------------

NAME = 'cdm'
GROUP = 'cdm'
VERSION = '1.0'
DESCRIPTION = 'Provides the cdm file system service'

# --------------------------------------------------------------------

@ioc.config
def server_uri():
    ''' The HTTP server URI, basically the URL where the content should be fetched from'''
    return '/content/'

@ioc.config
def repository_path():
    ''' The repository absolute or relative (to the distribution folder) path '''
    return path.join('workspace', 'shared', 'cdm')

@ioc.config
def use_linked_cdm():
    ''' Set to true when the files should not be copied into cdm'''
    return True

# --------------------------------------------------------------------
# Creating the content delivery managers

@ioc.entity
def delivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
    return d

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemLinkCDM() if use_linked_cdm() else LocalFileSystemCDM()
    cdm.delivery = delivery()
    return cdm

