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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

# --------------------------------------------------------------------

STATUSES = ['to do', 'in progress', 'done']

def createTaskStatus(label):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.query(TaskStatusMapped.id).filter(TaskStatusMapped.Key == label).one()[0]
    except NoResultFound:
        status = TaskStatusMapped()
        status.Key = label
        status.IsOn = True
        session.add(status)

    session.commit()
    session.close()

@app.populate
def populateTaskStatuses():
    for one_status in STATUSES:
        createTaskStatus(one_status)

