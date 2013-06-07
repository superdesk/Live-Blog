'''
Created on June 7, 2013

@package: superdesk livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugur

Contains upgrade functions
'''

from ..superdesk.db_superdesk import alchemySessionCreator
from ally.container import app
from ally.container.support import entityFor
from sqlalchemy.orm.session import Session
from superdesk.collaborator.api.collaborator import ICollaboratorService, \
    Collaborator
from superdesk.source.api.source import ISourceService, QSource, Source

# --------------------------------------------------------------------

def insertSMSSource():
    sourcesService = entityFor(ISourceService)
    assert isinstance(sourcesService, ISourceService)
    srcs = sourcesService.getAll(q=QSource(name='sms'))
    if srcs: src = next(srcs).Id
    else:
        src = Source()
        src.Name = 'sms'
        src.IsModifiable, src.URI, src.Type, src.Key = False, '', '', ''
        src = sourcesService.insert(src)

    collaboratorService = entityFor(ICollaboratorService)
    assert isinstance(collaboratorService, ICollaboratorService)
    colls = collaboratorService.getAll(qs=QSource(name='sms'))
    if not colls:
        coll = Collaborator()
        coll.User = None
        coll.Source = src
        collaboratorService.insert(coll)


@app.populate
def upgradeLiveBlog14():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    # set remove provider from blog source
    session.execute("ALTER TABLE livedesk_blog_source DROP FOREIGN KEY livedesk_blog_source_ibfk_3")
    session.execute("ALTER TABLE livedesk_blog_source DROP COLUMN fk_provider")

    # set collaborator table character set
    session.execute("ALTER TABLE collaborator CHARACTER SET utf8")

    # add phone number column to person
    session.execute("ALTER TABLE person ADD COLUMN phone_number VARCHAR(255) UNIQUE")

    # add unique constraint to source
    session.execute("ALTER TABLE source ADD UNIQUE uix_source_type_name (`name`, `fk_type_id`)")

    # add origin name column to source
    session.execute("ALTER TABLE source ADD COLUMN origin_name VARCHAR(255)")

    # add origin URI column to source
    session.execute("ALTER TABLE source ADD COLUMN origin_uri VARCHAR(255)")

    # add unique constraint to user
    session.execute("ALTER TABLE user ADD UNIQUE uix_user_name (`name`)")

    insertSMSSource()
