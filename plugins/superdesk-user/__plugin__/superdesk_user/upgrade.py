'''
Created on July 7, 2014

@package: superdesk user
@copyright: 2014 Sourcefabric o.p.s.
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
def upgradeUserCid():
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.execute("ALTER TABLE user CHANGE COLUMN `cid` `cid` BIGINT UNSIGNED DEFAULT 0")
    except (ProgrammingError, OperationalError): pass

    session.commit()
    session.close()

