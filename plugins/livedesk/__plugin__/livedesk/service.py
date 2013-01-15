'''
Created on Jan 9, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for livedesk.
'''

from ..plugin.registry import addService
from ally.container import support, ioc
from ..superdesk.db_superdesk import bindSuperdeskSession, bindSuperdeskValidations
from livedesk.impl.blog_theme import BlogThemeServiceAlchemy
from livedesk.api.blog_theme import IBlogThemeService
from cdm.impl.local_filesystem import IDelivery, HTTPDelivery, \
    LocalFileSystemCDM
from __plugin__.cdm.local_cdm import server_uri, repository_path
from cdm.spec import ICDM

# --------------------------------------------------------------------

SERVICES = 'livedesk.api.**.I*Service'

support.createEntitySetup('livedesk.impl.**.*')
support.bindToEntities('livedesk.impl.**.*Alchemy', binders=bindSuperdeskSession)
support.listenToEntities(SERVICES, listeners=addService(bindSuperdeskSession, bindSuperdeskValidations))
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

@ioc.entity
def delivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
    return d

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM();
    cdm.delivery = delivery()
    return cdm

@ioc.replace(ioc.getEntity(IBlogThemeService))
def themeService() -> IBlogThemeService:
    s = BlogThemeServiceAlchemy()
    s.cdmGUI = contentDeliveryManager()
    return s
