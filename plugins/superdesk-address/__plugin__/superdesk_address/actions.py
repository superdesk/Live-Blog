'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

#from ally.container import ioc
#from gui.action.api.action import Action
#from ..gui_action.service import actionManagerService
#from ..gui_action import defaults
#import __plugin__.superdesk_person.actions as personActions
#from ..gui_core.gui_core import getPublishedGui
#from ally.internationalization import NC_
#
## --------------------------------------------------------------------
#
#@ioc.entity   
#def menuAction():
#    scriptPath = getPublishedGui('superdesk/address/scripts/js/menu.js')
#    return Action('address', Parent=defaults.menuAction(), Label=NC_('Menu', 'Adresses'), ScriptPath=scriptPath)
#
#@ioc.entity   
#def modulesAction():
#    scriptPath = getPublishedGui('superdesk/address/scripts/js/modules.js')
#    return Action('address', Parent=defaults.modulesAction(), ScriptPath=scriptPath)
#
#@ioc.entity
#def personAction():
#    scriptPath = getPublishedGui('superdesk/address/scripts/js/person-user.js')
#    return Action('address', Parent=personActions.userAction(), ScriptPath=scriptPath)
#
#@ioc.start
#def registerActions():
#    actionManagerService().add(menuAction())
#    actionManagerService().add(modulesAction())
#    actionManagerService().add(personAction())
