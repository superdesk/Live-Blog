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
from internationalization.core.impl.po_file_manager import POFileManager
from internationalization.core.spec import IPOFileManager
from internationalization.impl.po_file import POFileService
from internationalization.scanner import Scanner
from internationalization.api.json_locale import IJSONLocaleFileService
from internationalization.impl.json_locale import JSONFileService

# --------------------------------------------------------------------

API, IMPL = 'internationalization.api.**.I*Service', 'internationalization.impl.**.*'

support.createEntitySetup(API, IMPL)
support.bindToEntities(IMPL, binders=bindInternationalizationSession)
support.listenToEntities(IMPL, listeners=addService(bindInternationalizationSession, bindInternationalizationValidations))
support.wireEntities(Scanner, POFileManager, POFileService)
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
def cdmLocale() -> ICDM:
    '''
    The content delivery manager (CDM) for the locale files.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'cache/locale/%s')

@ioc.entity
def poFileManager() -> IPOFileManager: return POFileManager()

@ioc.entity
def poFileService() -> IPOFileService:
    srv = POFileService()
    srv.cdmLocale = cdmLocale()
    return srv

@ioc.entity
def jsonFileService() -> IJSONLocaleFileService:
    srv = JSONFileService()
    srv.cdmLocale = cdmLocale()
    return srv

# --------------------------------------------------------------------

@ioc.after(createTables)
def scan():
    if scan_localized_messages():
        scanner().scanComponents()
        scanner().scanPlugins()
