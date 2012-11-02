'''
Created on Jan 9, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setup for internationalization.
'''
from sys import modules
from ..cdm.local_cdm import contentDeliveryManager
from ..plugin.registry import addService
from .db_internationalization import bindInternationalizationSession, \
    bindInternationalizationValidations, createTables
from ally.container import support, ioc
from cdm.spec import ICDM
from cdm.support import ExtendPathCDM
from internationalization.api.po_file import IPOFileService
from internationalization.impl.po_file import POFileService
from internationalization.scanner import Scanner
from internationalization.api.json_locale import IJSONLocaleFileService
from internationalization.impl.json_locale import JSONFileService

# --------------------------------------------------------------------

SERVICES = 'internationalization.api.**.I*Service'

support.createEntitySetup('internationalization.impl.**.*')
support.createEntitySetup('internationalization.*.impl.**.*')
support.bindToEntities('internationalization.impl.**.*Alchemy', binders=bindInternationalizationSession)
support.listenToEntities(SERVICES, listeners=addService(bindInternationalizationValidations), beforeBinding=False)
support.loadAllEntities(SERVICES)

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

@ioc.replace(ioc.getEntity(IPOFileService, modules[__name__]))
def poFileService() -> IPOFileService:
    srv = POFileService()
    srv.cdmLocale = cdmLocale()
    return srv

@ioc.replace(ioc.getEntity(IJSONLocaleFileService))
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
