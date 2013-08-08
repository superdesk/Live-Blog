''',
Created on May 3rd, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Publish the GUI resources.
'''

from ..gui_core.gui_core import cdmGUI
from ..livedesk_embed.gui import themes_path
from ally.container import app
from ally.container.support import entityFor
from livedesk.api.blog_theme import IBlogThemeService, QBlogTheme, BlogTheme
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@app.populate
def insertThemes():
    s = entityFor(IBlogThemeService)
    assert isinstance(s, IBlogThemeService)
    for name in ('default', 'tageswoche', 'stt', 'genapp', 'big-screen', 'zeit', 'zeit_solo'):
        q = QBlogTheme()
        q.name = name
        l = s.getAll(q=q)
        if not l:
            t = BlogTheme()
            t.Name = name
            t.URL = cdmGUI().getURI(themes_path() + '/' + name, 'http')
            t.IsLocal = True
            s.insert(t)
