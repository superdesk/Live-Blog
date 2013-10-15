'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Actions and acl action setups.
'''

# TODO: add to config XML
# from ..acl import gui
# from ..gui_action.service import addAction
# from ..gui_core.gui_core import publishedURI
# from ..media_archive.actions import modulesTypesAction as mediaArchiveAction
# from ally.container import ioc, support
# from gui.action.api.action import Action
# from superdesk.media_archive.api.image_data import IImageDataService
# from superdesk.media_archive.api.image_info import IImageInfoService
# from ally.internationalization import NC_
# from acl.right_action import RightAction
#
# # --------------------------------------------------------------------
#
# support.listenToEntities(Action, listeners=addAction)
# support.loadAllEntities(Action)
#
# # --------------------------------------------------------------------
#
# @ioc.entity
# def modulesAction() -> Action:
#     '''
#     register image plugin on media archive actions
#     '''
#     return Action('image', Parent=mediaArchiveAction(), Script=publishedURI('media-archive-image/scripts/js/media-archive/'))
#
# # --------------------------------------------------------------------
#
# @ioc.entity
# def rightMediaArchiveImageView() -> RightAction:
#     return gui.actionRight(NC_('security', 'IAM Image view'), NC_('security', '''
#     Allows read only access to IAM Image items.'''))
#
# # --------------------------------------------------------------------
#
# @gui.setup
# def registerAclMediaArchiveImageView():
#     r = rightMediaArchiveImageView()
#     r.addActions(modulesAction())
#     r.all(IImageDataService, IImageInfoService)
