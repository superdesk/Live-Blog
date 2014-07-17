'''
Created on July 16, 2014

@package: superdesk livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains upgrade functions
'''

from ..superdesk.db_superdesk import alchemySessionCreator
from ally.container import app
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy.orm.session import Session
from ally.container.app import PRIORITY_LAST

# --------------------------------------------------------------------

@app.populate(priority=PRIORITY_LAST)
def upgradeBlogSyncCid():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.execute("ALTER TABLE livedesk_blog_sync CHANGE COLUMN `id_change` `id_change` BIGINT UNSIGNED")
    except (ProgrammingError, OperationalError): pass

    session.commit()
    session.close()

