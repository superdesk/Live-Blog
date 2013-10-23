'''
Created on May 1, 2013

@package: frontline inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Populates default data for the services.
'''

from ally.container import app, ioc
from ..superdesk.db_superdesk import alchemySessionCreator
from superdesk.source.meta.type import SourceTypeMapped
from superdesk.post.meta.type import PostTypeMapped
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import exists

# --------------------------------------------------------------------

@ioc.config
def sms_source_types():
    ''' The source types used during SMS processing '''
    return ['smssource', 'smsprovider'] 

@ioc.config
def sms_post_types():
    ''' The post types used during SMS processing '''
    return ['normal']

def createSourceType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    if not session.query(exists().where(SourceTypeMapped.Key == key)).scalar():
        sourceTypeDb = SourceTypeMapped()
        sourceTypeDb.Key = key
        session.add(sourceTypeDb)

    session.commit()
    session.close()

def createPostType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    if not session.query(exists().where(PostTypeMapped.Key == key)).scalar():
        postTypeDb = PostTypeMapped()
        postTypeDb.Key = key
        session.add(postTypeDb)

    session.commit()
    session.close()

@app.populate
def populateTypes():
    for oneSourceType in sms_source_types():
        createSourceType(oneSourceType)

    for onePostType in sms_post_types():
        createPostType(onePostType)

