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
from __plugin__.cdm.local_cdm import contentDeliveryManager
from __plugin__.livedesk_embed.gui import themes_path

# --------------------------------------------------------------------

SERVICES = 'livedesk.api.**.I*Service'

support.createEntitySetup('livedesk.impl.**.*')
support.bindToEntities('livedesk.impl.**.*Alchemy', binders=bindSuperdeskSession)
support.listenToEntities(SERVICES, listeners=addService(bindSuperdeskSession, bindSuperdeskValidations))
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

@ioc.replace(ioc.getEntity(IBlogThemeService))
def themeService() -> IBlogThemeService:
    s = BlogThemeServiceAlchemy()
    s.themesPath = themes_path()
    s.cdmGUI = contentDeliveryManager()
    return s
