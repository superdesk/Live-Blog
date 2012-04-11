'''
Created on Jan 9, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setup for internationalization.
'''

from ..plugin.registry import addService
from .db_internationalization import bindInternationalizationSession, \
    bindInternationalizationValidations, createTables
from ally.container import support, ioc
from internationalization.scanner import Scanner
from internationalization.core.impl.po_file_manager import POFileManagerDB
from os import path
from cdm.impl.local_filesystem import IDelivery, HTTPDelivery, LocalFileSystemCDM
from ally.container._impl.ioc_setup import ConfigError
from cdm.spec import ICDM
from internationalization.api.po_file import IPOFileService
from internationalization.impl.po_file import POFileServiceCDM

# --------------------------------------------------------------------

API, IMPL = 'internationalization.api.**.I*Service', 'internationalization.impl.**.*'

support.createEntitySetup(API, IMPL)
support.bindToEntities(IMPL, binders=bindInternationalizationSession)
support.listenToEntities(IMPL, listeners=addService(bindInternationalizationSession, bindInternationalizationValidations))
support.wireEntities(Scanner, POFileManagerDB)
support.loadAllEntities(API)

# --------------------------------------------------------------------

@ioc.config
def scan_localized_messages():
    '''Flag indicating that the application should be scanned for localized messages'''
    return False

@ioc.config
def po_server_uri():
    ''' The HTTP server URI, basically the URL where the content should be fetched from'''
    return '/po/'

@ioc.config
def po_repository_path():
    ''' The PO repository absolute or relative (to the distribution folder) path '''
    return path.join('workspace', 'po_cdm')

# --------------------------------------------------------------------

@ioc.entity
def scanner(): return Scanner()

@ioc.entity
def poDelivery() -> IDelivery:
    if not po_repository_path():
        raise ConfigError('Missing repository path configuration')
    d = HTTPDelivery()
    d.serverURI = po_server_uri()
    d.repositoryPath = po_repository_path()
    return d

@ioc.entity
def poContentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM();
    cdm.delivery = poDelivery()
    return cdm

@ioc.entity
def poFileManager(): return POFileManagerDB()

@ioc.entity
def poFileServiceCDM() -> IPOFileService:
    srv = POFileServiceCDM()
    srv.poManager = poFileManager()
    srv.poCdm = poContentDeliveryManager()
    return srv

# --------------------------------------------------------------------

@ioc.after(createTables)
def scan():
    if scan_localized_messages():
        scanner().scanComponents()
        scanner().scanPlugins()
