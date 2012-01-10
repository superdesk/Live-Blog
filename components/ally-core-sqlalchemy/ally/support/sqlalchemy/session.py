'''
Created on Jan 5, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy automatic session handling.
'''

from _abcoll import Callable
from ally.api.configure import ServiceSupport
from ally.exception import DevelException
from ally.listener.binder import registerProxyBinder, bindBeforeListener, \
    bindAfterListener, bindExceptionListener, indexAfter, INDEX_LOCK_BEGIN, \
    indexBefore, INDEX_LOCK_END
from ally.support.util import AttributeOnThread
from collections import deque
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

ATTR_SESSION_CREATE = AttributeOnThread(__name__, 'session_create', deque)
# Attribute used for storing the session creator on the thread
ATTR_SESSION = AttributeOnThread(__name__, 'session', dict)
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

def beginWith(sessionCreator):
    '''
    Begins a session (on demand) based on the provided session creator for this thread.
    
    @param sessionCreator: class
        The session creator class.
    '''
    assert issubclass(sessionCreator, Session), 'Invalid session creator %s' % sessionCreator
    creators = ATTR_SESSION_CREATE.get(None)
    if not creators: creators = ATTR_SESSION_CREATE.set(deque())
    assert isinstance(creators, deque)
    creators.append(sessionCreator)

def openSession():
    '''
    Function to provide the session on the current thread, this will automatically create a session based on the current 
    thread session creator if one is not already created.
    '''
    creators = ATTR_SESSION_CREATE.get(None)
    if not creators: raise DevelException('Invalid call, it seems that the thread is not tagged with an SQL session')
    creator = creators[-1]
    creatorId = id(creator)
    sessions = ATTR_SESSION.get(None)
    if not sessions:
        session = creator()
        ATTR_SESSION.set({creatorId:session})
    else:
        session = sessions.get(creatorId)
        if not session:
            session = sessions[creatorId] = creator()
            assert log.debug('Created SQL Alchemy session') or True
    return session

def endCurrent(sessionCloser=None):
    '''
    Ends the transaction for the current thread session creator.
    
    @param sessionCloser: Callable|None
        A Callable that will be invoked for the ended transaction. It will take as a parameter the session to be closed.
    '''
    assert not sessionCloser or isinstance(sessionCloser, Callable), 'Invalid session closer %s' % sessionCloser
    creators = ATTR_SESSION_CREATE.get(None)
    if not creators: raise DevelException('Illegal end transaction call, there is no transaction begun')
    assert isinstance(creators, deque)
    creator = creators.pop()
    
    if not creators: ATTR_SESSION_CREATE.clear()
    
    if not ATTR_KEEP_ALIVE.get(False):
        sessions = ATTR_SESSION.get(None)
        if not sessions: ATTR_SESSION.clear()
        if sessions:
            session = sessions.pop(id(creator), None)
            if session and sessionCloser: sessionCloser(session)

def endAll(sessionCloser=None):
    '''
    Ends all the transaction for the current thread session.
    
    @param sessionCloser: Callable|None
        A Callable that will be invoked for the ended transactions. It will take as a parameter the session to be closed.
    '''
    assert not sessionCloser or isinstance(sessionCloser, Callable), 'Invalid session closer %s' % sessionCloser
    creators, sessions = ATTR_SESSION_CREATE.get(None), ATTR_SESSION.get(None)
    if sessions:
        while creators:
            creator = creators.pop()
            
            session = sessions.pop(id(creator), None)
            if session and sessionCloser: sessionCloser(session)
    ATTR_SESSION_CREATE.clear()
    ATTR_SESSION.clear()
    
# --------------------------------------------------------------------

def commit(session):
    '''
    Commit the session.
    
    @param session: Session
        The session to be committed.
    '''
    assert isinstance(session, Session), 'Invalid session %s' % session
    try:
        session.expunge_all()
        session.commit()
        assert log.debug('Committed SQL Alchemy session transactions') or True
    except InvalidRequestError:
        assert log.debug('Nothing to commit on SQL Alchemy session') or True
    assert log.debug('Properly closed SQL Alchemy session') or True

def rollback(session):
    '''
    Roll back the session.
    
    @param session: Session
        The session to be rolled back.
    '''
    assert isinstance(session, Session), 'Invalid session %s' % session
    session.rollback()
    assert log.debug('Improper SQL Alchemy session, rolled back transactions') or True

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
    registerProxyBinder(proxy)
    
    def begin(*args): beginWith(sessionCreator)
    def end(*args): endCurrent(commit)
    def exception(*args): endCurrent(rollback)
    
    bindBeforeListener(proxy, begin, index=INDEX_SESSION_BEGIN)
    bindAfterListener(proxy, end, index=INDEX_SESSION_END)
    bindExceptionListener(proxy, exception, index=INDEX_SESSION_END)
