'''
Created on April 9, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Populates sample data for the services.
'''

from ally.container import app
from ..superdesk.db_superdesk import alchemySessionCreator
from superdesk.desk.meta.task_status import TaskStatusMapped
from superdesk.desk.meta.task_link_type import TaskLinkTypeMapped
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

# --------------------------------------------------------------------

STATUSES = ['to do', 'in progress', 'done']
LINK_TYPES = ['is related to', 'depends on', 'is required by', 'duplicates', 'is duplicated by']

def createTaskStatus(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.query(TaskStatusMapped.id).filter(TaskStatusMapped.Key == key).one()[0]
    except NoResultFound:
        status = TaskStatusMapped()
        status.Key = key
        status.IsOn = True
        session.add(status)

    session.commit()
    session.close()

def createTaskLinkType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.query(TaskLinkTypeMapped.id).filter(TaskLinkTypeMapped.Key == key).one()[0]
    except NoResultFound:
        link_type = TaskLinkTypeMapped()
        link_type.Key = key
        link_type.IsOn = True
        session.add(link_type)

    session.commit()
    session.close()

@app.populate
def populateTaskStatuses():
    for one_status in STATUSES:
        createTaskStatus(one_status)

    for one_link_type in LINK_TYPES:
        createTaskLinkType(one_link_type)
