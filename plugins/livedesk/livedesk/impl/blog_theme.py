'''
Created on Jan 11, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the implementation of the blog theme API.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from livedesk.api.blog_theme import IBlogThemeService, QBlogTheme, BlogTheme
from ally.api.type import Iter
from ally.container import wire
from glob import glob
from os.path import join, isdir, isfile, basename, isabs
from ally.exception import InputError, Ref
from cdm.spec import ICDM
from ally.internationalization import _

# --------------------------------------------------------------------

@injected
@setup(IBlogThemeService)
class BlogThemeServiceAlchemy(IBlogThemeService):
    '''
    Implementation for @see: IBlogThemeService
    '''
    themes_path = 'lib/livedesk-embed/themes'; wire.config('themes_path')
    # The path to the themes directory

    cdmGUI = ICDM
    # The GUI resources CDM.

    def __init__(self):
        '''
        Construct the blog theme service.
        '''

    def getByKey(self, key:BlogTheme.Key) -> BlogTheme:
        '''
        @see IBlogThemeService.get
        '''
        return self._getTheme(join(self.themes_path, key))

    def getAll(self, offset:int=None, limit:int=None, q:QBlogTheme=None) -> Iter(BlogTheme):
        '''
        @see IBlogThemeService.getAll
        '''
        themesPath = self.cdmGUI.getURI(self.themes_path, 'file')
        if q and QBlogTheme.key in q and q.key:
            files = glob(join(themesPath, '*%s*' % q.key))
        else: files = glob(join(themesPath, '*'))
        for file in files:
            if not isdir(file): continue
            try:
                yield self._getTheme(file)
            except InputError: pass

    def insert(self, entity:BlogTheme) -> BlogTheme.Key:
        '''
        @see IBlogThemeService.insert
        '''

    def update(self, entity:BlogTheme) -> None:
        '''
        @see IBlogThemeService.update
        '''

    def delete(self, key:BlogTheme.Key) -> bool:
        '''
        @see IBlogThemeService.delete
        '''

    def _getTheme(self, path):
        if not isabs(path): path = self.cdmGUI.getURI(path, 'file')
        if isdir(path) and isfile('%s.js' % path):
            theme = BlogTheme()
            theme.Key = basename(path)
            theme.URL = self.cdmGUI.getURI(join(self.themes_path, theme.Key))
            return theme
        raise InputError(Ref(_('No such theme'), ref=BlogTheme.Key))
