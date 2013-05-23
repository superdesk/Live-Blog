'''
Created on May 21, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Populates default data for the services.
'''

from ally.container import app, ioc
from ..superdesk.db_superdesk import alchemySessionCreator
from content.article.meta.target_type import TargetTypeMapped
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import exists

# --------------------------------------------------------------------

@ioc.config
def output_target_types():
    ''' The output target types used during article publishing '''
    return ['web', 'tablet', 'mobile', 'General NewsML', 'Sports NewsML']

def createTargetType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    if not session.query(exists().where(TargetTypeMapped.Key == key)).scalar():
        targetTypeDb = TargetTypeMapped()
        targetTypeDb.Key = key
        session.add(targetTypeDb)

    session.commit()
    session.close()

@app.populate
def populateTypes():
    for oneTargetType in output_target_types():
        createTargetType(oneTargetType)

