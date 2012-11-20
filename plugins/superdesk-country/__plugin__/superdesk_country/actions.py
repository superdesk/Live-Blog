'''
Created on March 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

#from ally.container import ioc
#from ally.internationalization import NC_
#from gui.action.api.action import Action
#from ..gui_action.service import actionManagerService
#from ..gui_action import defaults
#from ..gui_core.gui_core import getPublishedGui
#
## --------------------------------------------------------------------
#
#@ioc.entity   
#def menuAction():
#    return Action('country', Parent=defaults.menuAction(), Label=NC_('Menu', 'Countries'),
#                  ScriptPath=getPublishedGui('superdesk/country/scripts/js/menu.js'), Href='/country/list')
#
#@ioc.entity   
#def modulesAction():
#    return Action('country', Parent=defaults.modulesAction())
#
#@ioc.entity   
#def modulesUpdateAction():
#    return Action('update', Parent=modulesAction(), 
#                  ScriptPath=getPublishedGui('superdesk/country/scripts/js/update.js'))
#
#@ioc.entity   
#def modulesListAction():
#    return Action('list', Parent=modulesAction(), 
#                  ScriptPath=getPublishedGui('superdesk/country/scripts/js/list.js'))
#
#@ioc.entity   
#def modulesAddAction():
#    return Action('add', Parent=modulesAction(), 
#                  ScriptPath=getPublishedGui('superdesk/country/scripts/js/add.js'))
#
#@ioc.start
#def registerActions():
#    actionManagerService().add(menuAction())
#    actionManagerService().add(modulesAction())
#    actionManagerService().add(modulesUpdateAction())
#    actionManagerService().add(modulesListAction())
#    actionManagerService().add(modulesAddAction())
