'''
Created on Jan 9, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setup for internationalization.
'''

from ..cdm.local_cdm import contentDeliveryManager
from ..plugin.registry import addService
from .db_internationalization import bindInternationalizationSession, \
    bindInternationalizationValidations, createTables
from ally.container import support, ioc
from cdm.spec import ICDM
from cdm.support import ExtendPathCDM
from internationalization.api.po_file import IPOFileService
from internationalization.core.impl.po_file_manager import POFileManagerDB
from internationalization.core.spec import IPOFileManager
from internationalization.impl.po_file import POFileServiceCDM
from internationalization.scanner import Scanner

# --------------------------------------------------------------------

API, IMPL = 'internationalization.api.**.I*Service', 'internationalization.impl.**.*'

support.createEntitySetup(API, IMPL)
support.bindToEntities(IMPL, binders=bindInternationalizationSession)
support.listenToEntities(IMPL, listeners=addService(bindInternationalizationSession, bindInternationalizationValidations))
support.wireEntities(Scanner, POFileManagerDB, POFileServiceCDM)
support.loadAllEntities(API)

# --------------------------------------------------------------------

@ioc.config
def scan_localized_messages():
    '''Flag indicating that the application should be scanned for localized messages'''
    return False

# --------------------------------------------------------------------

@ioc.entity
def scanner(): return Scanner()

@ioc.entity
def cdmPO() -> ICDM:
    '''
    The content delivery manager (CDM) for the PO generated files.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'cache/locale/%s')

@ioc.entity
def poFileManager() -> IPOFileManager: return POFileManagerDB()

@ioc.entity
def poFileServiceCDM() -> IPOFileService:
    srv = POFileServiceCDM()
    srv.cdmPO = cdmPO()
    return srv

# --------------------------------------------------------------------

@ioc.after(createTables)
def scan():
    if scan_localized_messages():
        scanner().scanComponents()
        scanner().scanPlugins()
