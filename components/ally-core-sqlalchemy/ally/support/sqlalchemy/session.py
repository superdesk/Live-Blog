'''
Created on Jan 5, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy automatic session handling.
'''

from ally.api.configure import ServiceSupport
from ally.listener.binder import registerProxyBinder, bindBeforeListener, \
    bindAfterListener, bindExceptionListener, indexAfter, INDEX_LOCK_BEGIN, \
    indexBefore, INDEX_LOCK_END
from ally.support.util import AttributeOnThread
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

ATTR_SESSION_CREATE = AttributeOnThread(__name__, 'session_create')
# Attribute used for storing the session creator on the thread
ATTR_SESSION = AttributeOnThread(__name__, 'session')
# Attribute used for storing the session on the thread
ATTR_KEEP_ALIVE = AttributeOnThread(__name__, 'session_alive', bool)
# Attribute used for storing the flag that indicates if a session should be closed or kept alive after a call. 

INDEX_SESSION_BEGIN = indexAfter('sql_session_begin', INDEX_LOCK_BEGIN)
# The sql session begin index.
INDEX_SESSION_END = indexBefore('sql_session_end', INDEX_LOCK_END)
# The sql session end index.

# --------------------------------------------------------------------

class SessionSupport:
    '''
    Class that provides for the services that use SQLAlchemy the session support.
    All services that use SQLAlchemy have to extend this class in order to provide the sql alchemy session
    of the request, the session will be automatically handled by the session processor.
    '''
    
    session = Session
    
    def __init__(self):
        '''
        Bind the session method.
        '''
        self.session = openSession
        if isinstance(self, ServiceSupport): ServiceSupport.__init__(self, self)


# --------------------------------------------------------------------

def register(sessionCreator):
    '''
    Register the provided session creator to this thread.
    
    @param sessionCreator: class
        The session creator class.
    '''
    assert issubclass(sessionCreator, Session), 'Invalid session creator %s' % sessionCreator
    ATTR_SESSION_CREATE.set(sessionCreator)

def openSession():
    '''
    Function to provide the session on the current thread, this will automatically create a session based on the thread
    session creator if one is not already created.
    '''
    session = ATTR_SESSION.get(None)
    if not session:
        sessionCreate = ATTR_SESSION_CREATE.get(None)
        if sessionCreate:
            session = sessionCreate()
            ATTR_SESSION.set(session)
            ATTR_SESSION_CREATE.delete()
            assert log.debug('Created SQL Alchemy session') or True
    assert session, 'Invalid call, it seems that the thread is not tagged with an SQL session'
    return session

def commit(session=None):
    '''
    Commit the current thread session.
    '''
    session = session or ATTR_SESSION.get(None)
    if session:
        assert isinstance(session, Session), 'Invalid session %s' % session
        try:
            session.commit()
            assert log.debug('Committed SQL Alchemy session transactions') or True
        except InvalidRequestError:
            assert log.debug('Nothing to commit on SQL Alchemy session') or True
        assert log.debug('Properly closed SQL Alchemy session') or True

def rollback(session=None):
    '''
    Roll back the current thread session.
    '''
    session = session or ATTR_SESSION.get(None)
    if session:
        assert isinstance(session, Session), 'Invalid session %s' % session
        session.rollback()
        assert log.debug('Improper SQL Alchemy session, rolled back transactions') or True

def close(session=None):
    '''
    Close the current thread session.
    '''
    session = session or ATTR_SESSION.get(None)
    if session:
        assert isinstance(session, Session), 'Invalid session %s' % session
        session.close()
    ATTR_SESSION.clear()
    ATTR_SESSION_CREATE.clear()
    ATTR_KEEP_ALIVE.clear()

# --------------------------------------------------------------------

def bindSession(proxy, sessionCreator):
    '''
    Binds a session creator wrapping for the provided proxy.
    
    @param proxy: @see: registerProxyBinder
        The proxy to bind the session creator to.
    @param sessionCreator: class
        The session creator class that will create the session.
    '''
    assert issubclass(sessionCreator, Session), 'Invalid session creator %s' % sessionCreator
    registerProxyBinder()
    
    def start(*args):
        register(sessionCreator)
    def end(*args):
        if not ATTR_KEEP_ALIVE.get(False):
            commit(); close()
    def exception(*args):
        rollback(); close()
    
    bindBeforeListener(proxy, start, index=INDEX_SESSION_BEGIN)
    bindAfterListener(proxy, end, index=INDEX_SESSION_END)
    bindExceptionListener(proxy, exception, index=INDEX_SESSION_END)
