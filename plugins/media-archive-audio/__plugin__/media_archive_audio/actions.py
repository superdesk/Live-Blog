'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Actions and acl action setups.
'''

# TODO: add to config XML
# from ..gui_core.gui_core import publishedURI
# from ..media_archive.actions import modulesAction as mediaArchiveAction
# from ally.container import ioc, support
# from ally.internationalization import NC_
# from gui.action.api.action import Action
# from superdesk.media_archive.api.audio_data import IAudioDataService
# from superdesk.media_archive.api.audio_info import IAudioInfoService
# from gui.action.meta.category_right import RightAction
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
#     return Action('audio', Parent=mediaArchiveAction(), Script=publishedURI('media-archive-audio/scripts/js/media-archive/'))
#
# # --------------------------------------------------------------------
#
# @ioc.entity
# def rightMediaArchiveAudioView() -> RightAction:
#     return gui.actionRight(NC_('security', 'IAM Audio view'), NC_('security', '''
#     Allows read only access to IAM Audio items.'''))
#
# # --------------------------------------------------------------------
#
# @gui.setup
# def registerAclMediaArchiveAudioView():
#     r = rightMediaArchiveAudioView()
#     r.addActions(modulesAction())
#     r.all(IAudioDataService, IAudioInfoService)
