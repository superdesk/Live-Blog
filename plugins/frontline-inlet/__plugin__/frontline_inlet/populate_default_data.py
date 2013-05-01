'''
Created on May 1, 2013

@package: frontline inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Populates default data for the services.
'''

from ally.container import app
from ..superdesk.db_superdesk import alchemySessionCreator
from superdesk.source.meta.type import SourceTypeMapped
from superdesk.post.meta.type import PostTypeMapped
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

# --------------------------------------------------------------------

SOURCE_TYPES = ('FrontlineSMS',)
POST_TYPES = ('normal',)

def createSourceType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.query(SourceTypeMapped.id).filter(SourceTypeMapped.Key == key).one()[0]
    except NoResultFound:
        sourceTypeDb = SourceTypeMapped()
        sourceTypeDb.Key = key
        session.add(sourceTypeDb)

    session.commit()
    session.close()

def createPostType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.query(PostTypeMapped.id).filter(PostTypeMapped.Key == key).one()[0]
    except NoResultFound:
        postTypeDb = PostTypeMapped()
        postTypeDb.Key = key
        session.add(postTypeDb)

    session.commit()
    session.close()

@app.populate
def populateTypes():
    for one_source_type in SOURCE_TYPES:
        createSourceType(one_source_type)

    for one_post_type in POST_TYPES:
        createPostType(one_post_type)

