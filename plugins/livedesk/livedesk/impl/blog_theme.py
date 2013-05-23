'''
Created on Jan 11, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the implementation of the blog theme API.
'''

from ally.cdm.spec import ICDM
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from livedesk.api.blog_theme import IBlogThemeService, QBlogTheme
from livedesk.meta.blog_theme import BlogThemeMapped
from sql_alchemy.impl.entity import EntityServiceAlchemy
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IBlogThemeService, name='blogThemeService')
class BlogThemeServiceAlchemy(EntityServiceAlchemy, IBlogThemeService):
    '''
    Implementation for @see: IBlogThemeService
    '''
    blogThemeCDM = ICDM; wire.entity('blogThemeCDM')
    # The GUI resources CDM.

    def __init__(self):
        '''
        Construct the blog theme service.
        '''
        EntityServiceAlchemy.__init__(self, BlogThemeMapped, QBlogTheme)

    def upload(self, content):
        '''
        @see IBlogThemeService.upload
        '''
        # TODO: implement blog theme upload
        return False

    def delete(self, id):
        '''
        @see IBlogThemeService.delete
        '''
        # TODO: implement deletion of the blog theme content if local
        return super().delete(id)
