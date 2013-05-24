'''
Created on May 3rd, 2012

@package: Livedesk
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Actions and acl action setups.
'''

from ..acl import gui
from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from acl.right_action import RightAction
from ally.container import ioc, support
from ally.internationalization import NC_
from gui.action.api.action import Action
from content.article.api.article import IArticleService

# --------------------------------------------------------------------

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

# --------------------------------------------------------------------

@ioc.entity
def menuAction() -> Action:
    return Action('article', Parent=defaults.menuAction(), Label=NC_('menu', 'Article'), NavBar='/article',
                  Script=publishedURI('superdesk/article/scripts/js/menu.js'))

@ioc.entity
def modulesAction() -> Action:
    return Action('article', Parent=defaults.modulesAction())

@ioc.entity
def modulesAddAction() -> Action:
    return Action('add', Parent=modulesAction(), Script=publishedURI('superdesk/article/scripts/js/add.js'))

@ioc.entity
def modulesEditAction() -> Action:
    return Action('edit', Parent=modulesAction(), Script=publishedURI('superdesk/article/scripts/js/edit.js'))

@ioc.entity
def modulesMainAction() -> Action:
    return Action('list', Parent=modulesAction(), Script=publishedURI('superdesk/article/scripts/js/list.js'))

# --------------------------------------------------------------------

@ioc.entity
def rightArticleView() -> RightAction:
    return gui.actionRight(NC_('security', 'Article view'), NC_('security', '''
    Allows read only access to Article.'''))

@ioc.entity
def rightArticleEdit() -> RightAction:
    return gui.actionRight(NC_('security', 'Article edit'), NC_('security', '''
    Allows read/write access to Article.'''))

# --------------------------------------------------------------------

@gui.setup
def registerAclArticleView():
    r = rightArticleView()
    r.addActions(menuAction(), modulesAction(), modulesMainAction(), modulesAddAction(), modulesEditAction())
    r.allGet(IArticleService)

@gui.setup
def registerAclArticleEdit():
    r = rightArticleEdit()
    r.addActions(menuAction(), modulesAction(), modulesMainAction(), modulesAddAction(), modulesEditAction())
    r.all(IArticleService)
