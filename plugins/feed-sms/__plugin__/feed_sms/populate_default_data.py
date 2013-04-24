'''
Created on April 24, 2013

@package: feed sms
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Populates sample data for the services.
'''

from ally.container import app
from ..superdesk.db_superdesk import alchemySessionCreator
from feed.sms.meta.sms_feed_type import SMSFeedTypeMapped
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

# --------------------------------------------------------------------

FEED_TYPES = ['other', 'local', 'event', 'politics',]

def createSMSFeedType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.query(SMSFeedTypeMapped.id).filter(SMSFeedTypeMapped.Key == key).one()[0]
    except NoResultFound:
        feed_type = SMSFeedTypeMapped()
        feed_type.Key = key
        feed_type.Active = True
        session.add(feed_type)

    session.commit()
    session.close()

@app.populate
def populateSMSFeedTypes():
    for one_feed_type in FEED_TYPES:
        createSMSFeedType(one_feed_type)
