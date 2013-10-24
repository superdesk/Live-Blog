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
from __plugin__.internationalization.db_internationalization import alchemySessionCreator as alchemySessionCreatorInternationalization
from internationalization.api.source import TYPE_PYTHON, TYPE_JAVA_SCRIPT, TYPE_HTML
from ally.container import app
from ally.container.support import entityFor
from livedesk.api.blog_theme import IBlogThemeService, QBlogTheme, BlogTheme
from livedesk.meta.blog_media import BlogMediaTypeMapped
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import exists
from superdesk.collaborator.api.collaborator import ICollaboratorService, \
    Collaborator
from superdesk.source.api.source import ISourceService, QSource, Source
from ally.container.app import PRIORITY_FINAL, PRIORITY_LAST
from __plugin__.livedesk.populate_default_data import createSourceType,\
    createUserType
from superdesk.user.meta.user_type import UserTypeMapped

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
def upgradeUser():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute('ALTER TABLE user ADD COLUMN active TINYINT(1) NOT NULL DEFAULT 1')
        session.execute('UPDATE user SET active = 1 WHERE deleted_on IS NULL')
        session.execute('UPDATE user SET active = 0 WHERE deleted_on IS NOT NULL')
    except (ProgrammingError, OperationalError): pass

    try: session.execute('ALTER TABLE user DROP COLUMN deleted_on')
    except (ProgrammingError, OperationalError): pass

@app.populate(priority=PRIORITY_LAST)
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

@app.populate
def upgradeInternationalizationSourceType():
    creator = alchemySessionCreatorInternationalization()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute("ALTER TABLE inter_source CHANGE `type` `type` ENUM('" + TYPE_PYTHON.replace("'", "''") + "', '" + TYPE_JAVA_SCRIPT.replace("'", "''") + "', '" + TYPE_HTML.replace("'", "''") + "')")
    except (ProgrammingError, OperationalError): pass

@app.populate
def upgradeLiveBlog14First():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.execute("ALTER TABLE user ADD COLUMN `fk_type_id` INT UNSIGNED")
    except (ProgrammingError, OperationalError): return
    session.execute("ALTER TABLE user ADD FOREIGN KEY `fk_type_id` (`fk_type_id`) REFERENCES `user_type` (`id`) ON DELETE RESTRICT")
    session.execute("UPDATE user, user_type SET user.fk_type_id = user_type.id WHERE user_type.key = 'standard'")
    session.execute("ALTER TABLE user CHANGE COLUMN `fk_type_id` `fk_type_id` INT UNSIGNED NOT NULL")

@app.populate(priority=PRIORITY_FINAL)
def upgradeLiveBlog14Last():
    insertTheme()
    insertSource('comments')
    createSourceType('comment')

@app.populate(priority=PRIORITY_FINAL)
def upgradeLiveBlog14End():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute('ALTER TABLE `post` CHANGE COLUMN `meta` `meta` TEXT NULL DEFAULT NULL, '
                        'CHANGE COLUMN `content_plain` `content_plain` TEXT NULL DEFAULT NULL, '
                        'CHANGE COLUMN `content` `content` TEXT NULL DEFAULT NULL')
    except (ProgrammingError, OperationalError): return

@app.populate(priority=PRIORITY_FINAL)
def upgradeMediaArchiveDeleteFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute('ALTER TABLE `archive_audio_data` DROP FOREIGN KEY `archive_audio_data_ibfk_1`')
        session.execute('ALTER TABLE `archive_audio_data` ADD CONSTRAINT `archive_audio_data_ibfk_1` '
                    'FOREIGN KEY (`fk_metadata_id` ) REFERENCES `archive_meta_data` (`id` ) '
                    'ON DELETE CASCADE ON UPDATE RESTRICT')
    except (ProgrammingError, OperationalError): pass

    try:
        session.execute('ALTER TABLE `archive_audio_info` DROP FOREIGN KEY `archive_audio_info_ibfk_1`')
        session.execute('ALTER TABLE `archive_audio_info` ADD CONSTRAINT `archive_audio_info_ibfk_1` '
                    'FOREIGN KEY (`fk_metainfo_id` ) REFERENCES `archive_meta_info` (`id` ) '
                    'ON DELETE CASCADE ON UPDATE RESTRICT')
    except (ProgrammingError, OperationalError): pass

    try:
        session.execute('ALTER TABLE `archive_image_data` DROP FOREIGN KEY `archive_image_data_ibfk_1`')
        session.execute('ALTER TABLE `archive_image_data` ADD CONSTRAINT `archive_image_data_ibfk_1` '
                    'FOREIGN KEY (`fk_metadata_id` ) REFERENCES `archive_meta_data` (`id` ) '
                    'ON DELETE CASCADE ON UPDATE RESTRICT')
    except (ProgrammingError, OperationalError): pass

    try:
        session.execute('ALTER TABLE `archive_image_info` DROP FOREIGN KEY `archive_image_info_ibfk_1`')
        session.execute('ALTER TABLE `archive_image_info` ADD CONSTRAINT `archive_image_info_ibfk_1` '
                    'FOREIGN KEY (`fk_metainfo_id` ) REFERENCES `archive_meta_info` (`id` ) '
                    'ON DELETE CASCADE ON UPDATE RESTRICT')
    except (ProgrammingError, OperationalError): pass

    try:
        session.execute('ALTER TABLE `archive_video_data` DROP FOREIGN KEY `archive_video_data_ibfk_1`')
        session.execute('ALTER TABLE `archive_video_data` ADD CONSTRAINT `archive_video_data_ibfk_1` '
                    'FOREIGN KEY (`fk_metadata_id` ) REFERENCES `archive_meta_data` (`id` ) '
                    'ON DELETE CASCADE ON UPDATE RESTRICT')
    except (ProgrammingError, OperationalError): pass

    try:
        session.execute('ALTER TABLE `archive_video_info` DROP FOREIGN KEY `archive_video_info_ibfk_1`')
        session.execute('ALTER TABLE `archive_video_info` ADD CONSTRAINT `archive_video_info_ibfk_1` '
                    'FOREIGN KEY (`fk_metainfo_id` ) REFERENCES `archive_meta_info` (`id` ) '
                    'ON DELETE CASCADE ON UPDATE RESTRICT')
    except (ProgrammingError, OperationalError): pass

def createBlogMediaType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    if not session.query(exists().where(BlogMediaTypeMapped.Key == key)).scalar():
        blogMediaTypeDb = BlogMediaTypeMapped()
        blogMediaTypeDb.Key = key
        session.add(blogMediaTypeDb)

    session.commit()
    session.close()

@app.populate(priority=PRIORITY_FINAL)
def upgradeBlogMedia():
    createBlogMediaType('top_banner')

@app.populate(priority=PRIORITY_FINAL)
def upgradeBlogSourceDeleteFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute('ALTER TABLE `livedesk_blog_source` DROP FOREIGN KEY `livedesk_blog_source_ibfk_2`')
    except (ProgrammingError, OperationalError): return
    session.execute('ALTER TABLE `livedesk_blog_source` ADD CONSTRAINT `livedesk_blog_source_ibfk_2` '
                'FOREIGN KEY (`fk_source` ) REFERENCES `source` (`id` ) '
                'ON DELETE RESTRICT ON UPDATE RESTRICT')

@app.populate(priority=PRIORITY_FINAL)
def upgradeSourceUnicityFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute('ALTER TABLE `source` DROP KEY `uix_source_type_name`')
    except (ProgrammingError, OperationalError): return
    session.execute('ALTER TABLE `source` ADD CONSTRAINT `uix_source_type_name` '
                'UNIQUE KEY (`name`, `fk_type_id`, `uri`)')
    
    
@app.populate(priority=PRIORITY_FINAL)
def upgradeUserTypeFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    
    createUserType('commentator')
    createUserType('sms')
    createUserType('chained blog')

    id = session.query(UserTypeMapped.id).filter(UserTypeMapped.Key == 'sms').scalar()
    session.execute('UPDATE user SET fk_type_id = ' + str(id) + ' WHERE name LIKE "SMS-%"')
    
    id = session.query(UserTypeMapped.id).filter(UserTypeMapped.Key == 'commentator').scalar()
    session.execute('UPDATE user SET fk_type_id = ' + str(id) + ' WHERE name LIKE "Comment-%"')
    
    id = session.query(UserTypeMapped.id).filter(UserTypeMapped.Key == 'chained blog').scalar()
    session.execute('UPDATE user SET fk_type_id = ' + str(id) + ' WHERE LENGTH(name) > 35')
    
    session.commit()
    
  
