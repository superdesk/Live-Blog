'''
Created on Jan 5, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy automatic session handling.
'''

from ally.container.impl.proxy import IProxyHandler, Execution, \
    registerProxyHandler
from ally.exception import DevelError
from collections import deque
from inspect import isgenerator
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session
from threading import current_thread
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class SessionSupport:
    '''
    Class that provides for the services that use SQLAlchemy the session support.
    All services that use SQLAlchemy have to extend this class in order to provide the sql alchemy session
    of the request, the session will be automatically handled by the session processor.
    '''

    def session(self):
        '''
        Provide or construct a session.
        '''
        return openSession()

# --------------------------------------------------------------------

def setKeepAlive(keep):
    '''
    Set the flag that indicates if a session should be closed or kept alive after a call has finalized.
    If the session is left opened then other processes need to close it.
    
    @param keep: boolean
        Flag indicating that the session should be left open (True) or not (False).
    '''
    assert isinstance(keep, bool), 'Invalid keep flag %s' % keep
    current_thread()._ally_db_session_alive = keep
    

def beginWith(sessionCreator):
    '''
    Begins a session (on demand) based on the provided session creator for this thread.
    
    @param sessionCreator: class
        The session creator class.
    '''
    assert issubclass(sessionCreator, Session), 'Invalid session creator %s' % sessionCreator
    try: creators = current_thread()._ally_db_session_create
    except AttributeError: creators = current_thread()._ally_db_session_create = deque()
    assert isinstance(creators, deque)
    creators.append(sessionCreator)
    assert log.debug('Begin session creator %s', sessionCreator) or True

def openSession():
    '''
    Function to provide the session on the current thread, this will automatically create a session based on the current 
    thread session creator if one is not already created.
    '''
    thread = current_thread()
    try: creators = thread._ally_db_session_create
    except AttributeError: raise DevelError('Invalid call, it seems that the thread is not tagged with an SQL session')
    creator = creators[-1]
    creatorId = id(creator)
    try: sessions = thread._ally_db_session
    except AttributeError:
        session = creator()
        thread._ally_db_session = {creatorId:session}
        assert log.debug('Created SQL Alchemy session %s', session) or True
    else:
        session = sessions.get(creatorId)
        if session is None:
            session = sessions[creatorId] = creator()
            assert log.debug('Created SQL Alchemy session %s', session) or True
    return session

def hasSession():
    '''
    Function to check if there is a session on the current thread.
    '''
    thread = current_thread()
    try: creators = thread._ally_db_session_create
    except AttributeError: raise DevelError('Invalid call, it seems that the thread is not tagged with an SQL session')
    creatorId = id(creators[-1])
    try: sessions = thread._ally_db_session
    except AttributeError: return False
    return creatorId in sessions

def endCurrent(sessionCloser=None):
    '''
    Ends the transaction for the current thread session creator.
    
    @param sessionCloser: Callable|None
        A Callable that will be invoked for the ended transaction. It will take as a parameter the session to be closed.
    '''
    assert not sessionCloser or callable(sessionCloser), 'Invalid session closer %s' % sessionCloser
    thread = current_thread()
    try: creators = thread._ally_db_session_create
    except AttributeError: raise DevelError('Illegal end transaction call, there is no transaction begun')
    assert isinstance(creators, deque)

    creator = creators.pop()
    assert log.debug('End session creator %s', creator) or True
    if not creators:
        if not getattr(current_thread(), '_ally_db_session_alive', False): endSessions(sessionCloser)
        del thread._ally_db_session_create

def endSessions(sessionCloser=None):
    '''
    Ends all the transaction for the current thread session.
    
    @param sessionCloser: Callable|None
        A Callable that will be invoked for the ended transactions. It will take as a parameter the session to be closed.
    '''
    assert not sessionCloser or callable(sessionCloser), 'Invalid session closer %s' % sessionCloser
    thread = current_thread()
    try: sessions = thread._ally_db_session
    except AttributeError: return
    while sessions:
        _creatorId, session = sessions.popitem()
        if sessionCloser: sessionCloser(session)
    del thread._ally_db_session
    assert log.debug('Ended all sessions') or True

# --------------------------------------------------------------------

def commit(session):
    '''
    Commit the session.
    
    @param session: Session
        The session to be committed.
    '''
    assert isinstance(session, Session), 'Invalid session %s' % session
    try:
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

def commitNow():
    '''
    Commits the current session right now.
    
    @return: boolean
        True if a session was commited, False otherwise.
    '''
    thread = current_thread()
    try: creators = thread._ally_db_session_create
    except AttributeError: return False
    creator = creators[-1]
    creatorId = id(creator)
    try: sessions = thread._ally_db_session
    except AttributeError: return False
    session = sessions.get(creatorId)
    if session is not None:
        commit(session)
        return True

# --------------------------------------------------------------------

def bindSession(proxy, sessionCreator):
    '''
    Binds a session creator wrapping for the provided proxy.
    
    @param proxy: Proxy
        The proxy to wrap with session creator.
    @param sessionCreator: class
        The session creator class that will create the session.
    '''
    registerProxyHandler(SessionBinder(sessionCreator), proxy)

# --------------------------------------------------------------------

class SessionBinder(IProxyHandler):
    '''
    Implementation for @see: IProxyHandler for binding sql alchemy session.
    '''
    __slots__ = ('sessionCreator',)
    
    def __init__(self, sessionCreator):
        '''
        Binds a session creator wrapping for the provided proxy.
    
        @param sessionCreator: class
            The session creator class that will create the session.
        '''
        assert issubclass(sessionCreator, Session), 'Invalid session creator %s' % sessionCreator
        self.sessionCreator = sessionCreator
    
    def handle(self, execution):
        '''
        @see: IProxyHandler.handle
        '''
        assert isinstance(execution, Execution), 'Invalid execution %s' % execution
        
        beginWith(self.sessionCreator)
        try: returned = execution.invoke()
        except:
            endCurrent(rollback)
            raise
        else:
            if hasSession():
                session = openSession()
                session.flush()
                session.expunge_all()
                endCurrent(commit)
            elif isgenerator(returned):
                # If the returned value is a generator we need to wrap it in order to provide session support when the actual
                # generator is used
                return self.wrapGenerator(returned)
            return returned

    # ----------------------------------------------------------------
    
    def wrapGenerator(self, generator):
        '''
        Wraps the generator with the session creator.
        '''
        assert isgenerator(generator), 'Invalid generator %s' % generator
        beginWith(self.sessionCreator)
        try:
            for item in generator: yield item
        except:
            endCurrent(rollback)
            raise
        else:
            endCurrent(commit)
