'''
Created on Feb 2, 2012

@package: introspection request
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Registered actions for request plugin
'''

from ..development.service import publish_development
from ..gui_action import defaults
from ..gui_action.defaults import actionManagerService
from ..gui_core.gui_core import getPublishedGui
from ally.container import ioc
from ally.internationalization import N_
from gui.action.api.action import Action

# --------------------------------------------------------------------

@ioc.entity
def menuAction():
    return Action('request', N_('Request'), Parent=defaults.menuAction(), Href='/api-requests',
               ScriptPath=getPublishedGui('superdesk/request/scripts/js/menu.js'))

@ioc.entity
def modulesAction():
    return Action('request', Parent=defaults.modulesAction())

@ioc.entity
def modulesListAction():
    return Action('list', N_('Request'), Parent=modulesAction(),
               ScriptPath=getPublishedGui('superdesk/request/scripts/js/list.js'))

#@ioc.start
def actionRegister():
    if publish_development():
        actionManagerService().add(menuAction())
        actionManagerService().add(modulesAction())
        actionManagerService().add(modulesListAction())

