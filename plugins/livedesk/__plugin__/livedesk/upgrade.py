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
from ally.container import app, support
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
from superdesk.user.meta.user import UserMapped
from uuid import uuid4
from superdesk.post.meta.post import PostMapped
from superdesk.source.meta.type import SourceTypeMapped
from superdesk.verification.meta.status import VerificationStatusMapped
from superdesk.general_setting.meta.general_setting import GeneralSettingMapped
from superdesk.general_setting.api.general_setting import GeneralSetting,\
    IGeneralSettingService

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

@app.populate(priority=PRIORITY_LAST)
def upgradeBlogPostCid():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.execute("ALTER TABLE livedesk_post CHANGE COLUMN `id_change` `id_change` BIGINT UNSIGNED")
    except (ProgrammingError, OperationalError): pass

    session.commit()
    session.close()

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
    
    session.commit()
    session.close()

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
    
    session.commit()
    session.close()

@app.populate
def upgradeInternationalizationSourceType():
    creator = alchemySessionCreatorInternationalization()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute("ALTER TABLE inter_source CHANGE `type` `type` ENUM('" + TYPE_PYTHON.replace("'", "''") + "', '" + TYPE_JAVA_SCRIPT.replace("'", "''") + "', '" + TYPE_HTML.replace("'", "''") + "')")
    except (ProgrammingError, OperationalError): pass
    
    session.commit()
    session.close()

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
    
    session.commit()
    session.close()

@app.populate(priority=PRIORITY_FINAL)
def upgradeLiveBlog14Last():
    #insertTheme()
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
    
    session.commit()
    session.close()

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
    
    session.commit()
    session.close()

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
    
    session.commit()
    session.close()

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
    session.commit()
    session.close()
    
@app.populate(priority=PRIORITY_FINAL)
def upgradeUserTypeFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    
    createUserType('sms')
    createUserType('chained blog')

    id = session.query(UserTypeMapped.id).filter(UserTypeMapped.Key == 'sms').scalar()
    session.execute('UPDATE user SET fk_type_id = ' + str(id) + ' WHERE name LIKE "SMS-%"')
    
    id = session.query(UserTypeMapped.id).filter(UserTypeMapped.Key == 'commentator').scalar()
    session.execute('UPDATE user SET fk_type_id = ' + str(id) + ' WHERE name LIKE "Comment-%"')
    
    id = session.query(UserTypeMapped.id).filter(UserTypeMapped.Key == 'chained blog').scalar()
    session.execute('UPDATE user SET fk_type_id = ' + str(id) + ' WHERE LENGTH(name) > 35')
    
    session.commit()
    session.close()
    
    
@app.populate(priority=PRIORITY_LAST)
def upgradeBlogFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        # add deleted on for blog in order to be able to hide archived blogs
        session.execute("ALTER TABLE  livedesk_blog ADD COLUMN deleted_on DATETIME")
    except (ProgrammingError, OperationalError): return
    
    session.commit()
    session.close() 

@app.populate(priority=PRIORITY_LAST)
def upgradePostFeedFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    
    try: session.execute("ALTER TABLE post ADD COLUMN fk_feed_id INT UNSIGNED")
    except (ProgrammingError, OperationalError): return
    session.execute("ALTER TABLE post ADD FOREIGN KEY fk_feed_id (fk_feed_id) REFERENCES source (id) ON DELETE RESTRICT")
    
    session.commit()
    session.close() 
    
@app.populate(priority=PRIORITY_FINAL)
def upgradeUuidFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    # add uuid column for post and user
    try:
        session.execute("ALTER TABLE  post ADD COLUMN uuid VARCHAR(32)")   
        session.execute("ALTER TABLE  user ADD COLUMN uuid VARCHAR(32) NULL UNIQUE")
        session.execute("ALTER TABLE  user ADD COLUMN cid int DEFAULT 0")
    except (ProgrammingError, OperationalError): return    
    
    session.commit()
    
    # init uuid column for post and user
    users= session.query(UserMapped.Id, UserMapped.Uuid).all()
    for user in users:
        if user.Uuid is None: user.Uuid = str(uuid4().hex)
    session.commit()
    
    posts= session.query(PostMapped.Id, PostMapped.Uuid).all()
    for post in posts:
        if post.Uuid is None: post.Uuid = str(uuid4().hex)
    session.commit()
    
    session.close() 
        
@app.populate(priority=PRIORITY_LAST)
def upgradeSyncBlogFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    
    try: 
        session.execute('ALTER TABLE livedesk_blog_sync DROP FOREIGN KEY livedesk_blog_sync_ibfk_3')
        session.execute("ALTER TABLE livedesk_blog_sync DROP COLUMN fk_user_id")
        session.execute("ALTER TABLE livedesk_blog_sync CHANGE sync_start last_activity DATETIME")
    except (ProgrammingError, OperationalError): pass
        
    try: session.execute('ALTER TABLE source DROP KEY uix_1')
    except (ProgrammingError, OperationalError): pass
    
    try: session.execute('ALTER TABLE person DROP KEY phone_number')
    except (ProgrammingError, OperationalError): pass
        
    try: session.execute("DROP TABLE livedesk_sms_sync")
    except (ProgrammingError, OperationalError): pass
    
    session.commit()
    session.close() 
    
@app.populate(priority=PRIORITY_FINAL)
def upgradeSourceSmsFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    

    try:
        if session.query(SourceTypeMapped.id).filter(SourceTypeMapped.Key == 'smsblog').count() == 0:
            session.execute('INSERT INTO source_type (`key`) values("smsblog")')
    except (Exception): pass 
    
    try:
        if session.query(SourceTypeMapped.id).filter(SourceTypeMapped.Key == 'smsfeed').count() == 0:
            session.execute('INSERT INTO source_type (`key`) values("smsfeed")')
    except (Exception): pass   
    
    try:   
        idSmsfeed = session.query(SourceTypeMapped.id).filter(SourceTypeMapped.Key == 'smsfeed').scalar()
        idFrontlineSMS = session.query(SourceTypeMapped.id).filter(SourceTypeMapped.Key == 'FrontlineSMS').scalar()     
        session.execute('UPDATE source SET fk_type_id =' + str(idSmsfeed) + ' WHERE fk_type_id=' + str(idFrontlineSMS))
    except (Exception): pass 
    
    try:
        if session.query(SourceTypeMapped.id).filter(SourceTypeMapped.Key == 'FrontlineSMS').count() > 0:
            session.execute('DELETE FROM source_type WHERE `key` ="FrontlineSMS"')
    except (Exception): pass
       
    session.commit()
    session.close() 
    
    
@app.populate(priority=PRIORITY_LAST)
def upgradePostWasPublishedFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    

    try:
        session.execute("ALTER TABLE post ADD COLUMN was_published TINYINT(1)")
    except (Exception): pass
    
    try:
        session.execute("UPDATE post SET was_published=0 WHERE published_on IS NULL")
        session.execute("UPDATE post SET was_published=1 WHERE published_on IS NOT NULL")
    except (Exception): pass
    
       
    session.commit()    
    session.close() 
    
    
@app.populate(priority=PRIORITY_FINAL)
def upgradePostVerificationFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    

    try:
        idNoStatus = session.query(VerificationStatusMapped.id).filter(VerificationStatusMapped.Key == 'nostatus').scalar()
        session.execute("INSERT INTO post_verification (fk_post_id, fk_user_id, fk_status_id) \
                         SELECT id, NULL, " + idNoStatus + " FROM post WHERE id not in (SELECT fk_post_id FROM post_verification) ")
    except (Exception): pass
       
    session.commit()
    session.close()
    
    
@app.populate(priority=PRIORITY_FINAL)
def upgradeUserUuidUniqueFix():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)


    idStandard = session.query(UserTypeMapped.id).filter(UserTypeMapped.Key == 'standard').scalar()
    idChained = session.query(UserTypeMapped.id).filter(UserTypeMapped.Key == 'chained blog').scalar()  

    # find duplicate uuid and set other value
    inSql = session.query(UserMapped.Uuid)
    inSql = inSql.filter(UserMapped.typeId == idStandard)
    
    sql = session.query(UserMapped.Id, UserMapped.Uuid)
    sql = sql.filter(UserMapped.typeId == idChained)
    sql = sql.filter(UserMapped.Uuid.in_(inSql))
    users= sql.all()
    
    for user in users:
        user.Uuid = str(uuid4().hex)
    session.commit()

    try:
        session.execute("ALTER TABLE `user` ADD UNIQUE INDEX `uuid` (`uuid` ASC)")
    except (Exception): pass
       
    session.commit()
    session.close()    
    
@app.populate(priority=PRIORITY_FINAL)
def populateVersionConfig(): 
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    
    generalSettingService = support.entityFor(IGeneralSettingService)
    assert isinstance(generalSettingService, IGeneralSettingService)    
    
    generalSetting = GeneralSetting()
    generalSetting.Group = 'version'
    
    
    if session.query(GeneralSettingMapped).filter(GeneralSettingMapped.Key == 'major').count() == 0:
        generalSetting.Key = 'major'
        generalSetting.Value = '1'
        generalSettingService.insert(generalSetting)  
    
    if session.query(GeneralSettingMapped).filter(GeneralSettingMapped.Key == 'minor').count() == 0:
        generalSetting.Key = 'minor'
        generalSetting.Value = '6'
        generalSettingService.insert(generalSetting) 
    
    if session.query(GeneralSettingMapped).filter(GeneralSettingMapped.Key == 'revision').count() == 0:
        generalSetting.Key = 'revision'
        generalSetting.Value = '0'
        generalSettingService.insert(generalSetting)    

@app.populate(priority=PRIORITY_FINAL)
def upgradeSeoChangedOnFix(): 
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try:
        session.execute("ALTER TABLE `livedesk_blog_seo` ADD COLUMN `changed_on` DATETIME NULL DEFAULT NULL")
    except (Exception): pass
        
