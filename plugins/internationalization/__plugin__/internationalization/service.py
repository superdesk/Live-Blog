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

# --------------------------------------------------------------------

API, IMPL = 'internationalization.api.**.I*Service', 'internationalization.impl.**.*'

support.createEntitySetup(API, IMPL)
support.bindToEntities(IMPL, binders=bindInternationalizationSession)
support.listenToEntities(IMPL, listeners=addService(bindInternationalizationSession, bindInternationalizationValidations))
support.wireEntities(Scanner)
support.loadAllEntities(API)

# --------------------------------------------------------------------

@ioc.config
def scan_localized_messages():
    '''Flag indicating that the application should be scanned for localized messages'''
    return False

# --------------------------------------------------------------------

@ioc.entity
def scanner(): return Scanner()

# --------------------------------------------------------------------

@ioc.after(createTables)
def scan():
    if scan_localized_messages():
        scanner().scanComponents()
        scanner().scanPlugins()
