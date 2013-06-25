'''
Created on June 7, 2013

@package: superdesk livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugur

Contains upgrade functions
'''

from ..gui_core.gui_core import cdmGUI
from ..livedesk_embed.gui import themes_path
from ..superdesk.db_superdesk import alchemySessionCreator
from ally.container import app
from ally.container.support import entityFor
from livedesk.api.blog_theme import IBlogThemeService, QBlogTheme, BlogTheme
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy.orm.session import Session
from superdesk.collaborator.api.collaborator import ICollaboratorService, \
    Collaborator
from superdesk.source.api.source import ISourceService, QSource, Source
from ally.container.app import PRIORITY_LAST, PRIORITY_FIRST
from __plugin__.livedesk.populate_default_data import createSourceType

# --------------------------------------------------------------------

def insertSource(name):
    sourcesService = entityFor(ISourceService)
    assert isinstance(sourcesService, ISourceService)
    srcs = sourcesService.getAll(q=QSource(name=name))
    if srcs: src = next(iter(srcs)).Id
    else:
        src = Source()
        src.Name = name
        src.IsModifiable, src.URI, src.Type, src.Key = False, '', '', ''
        src = sourcesService.insert(src)

    collaboratorService = entityFor(ICollaboratorService)
    assert isinstance(collaboratorService, ICollaboratorService)
    colls = collaboratorService.getAll(qs=QSource(name=name))
    if not colls:
        coll = Collaborator()
        coll.User = None
        coll.Source = src
        collaboratorService.insert(coll)

def insertTheme():
    s = entityFor(IBlogThemeService)
    assert isinstance(s, IBlogThemeService)
    for name in ('big-screen',):
        q = QBlogTheme(name=name)
        l = s.getAll(q=q)
        if not l:
            t = BlogTheme()
            t.Name = name
            t.URL = cdmGUI().getURI(themes_path() + '/' + name, 'http')
            t.IsLocal = True
            s.insert(t)

# --------------------------------------------------------------------

@app.populate
def upgradeLiveBlog14():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        # add phone number column to person
        session.execute("ALTER TABLE person ADD COLUMN phone_number VARCHAR(255) UNIQUE")
    except (ProgrammingError, OperationalError): return

    # set remove provider from blog source
    session.execute("ALTER TABLE livedesk_blog_source DROP FOREIGN KEY livedesk_blog_source_ibfk_3")
    session.execute("ALTER TABLE livedesk_blog_source DROP COLUMN fk_provider")

    # set collaborator table character set
    session.execute("ALTER TABLE collaborator CHARACTER SET utf8")

    # add unique constraint to source
    session.execute("ALTER TABLE source ADD UNIQUE uix_source_type_name (`name`, `fk_type_id`)")

    # add origin name column to source
    session.execute("ALTER TABLE source ADD COLUMN origin_name VARCHAR(255)")

    # add origin URI column to source
    session.execute("ALTER TABLE source ADD COLUMN origin_uri VARCHAR(255)")

    # add unique constraint to user
    session.execute("ALTER TABLE user ADD UNIQUE uix_user_name (`name`)")

    insertSource('sms')

@app.populate(priority=PRIORITY_FIRST)
def upgradeLiveBlog14First():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute("ALTER TABLE user ADD COLUMN `fk_type_id` INT UNSIGNED")
    except (ProgrammingError, OperationalError): return
    session.execute("ALTER TABLE user ADD FOREIGN KEY `fk_type_id` (`fk_type_id`) REFERENCES `user_type` (`id`) ON DELETE RESTRICT")
    session.execute("UPDATE user, user_type SET user.fk_type_id = user_type.id WHERE user_type.key = 'standard'")
    session.execute("ALTER TABLE user CHANGE COLUMN `fk_type_id` `fk_type_id` INT UNSIGNED NOT NULL")

@app.populate(priority=PRIORITY_LAST)
def upgradeLiveBlog14Last():
    insertTheme()
    insertSource('comments')
    createSourceType('comment')
