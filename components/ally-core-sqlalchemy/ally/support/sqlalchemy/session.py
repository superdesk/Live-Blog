'''
Created on Jan 5, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy automatic session handling.
'''

from ally.api.configure import ServiceSupport
from ally.support.util import Attribute
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session
from threading import current_thread
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

ATTR_SQL_SESSION = Attribute(__name__, 'session')
ATTR_SQL_SESSION_CREATE = Attribute(__name__, 'session_create')

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
        self.session = getSession
        if isinstance(self, ServiceSupport): ServiceSupport.__init__(self, self)
        
# --------------------------------------------------------------------

def getSession():
    '''
    Function to provide the session on the current thread.
    '''
    thread = current_thread()
    session = ATTR_SQL_SESSION.get(thread, None)
    if not session:
        sessionCreate = ATTR_SQL_SESSION_CREATE.get(thread, None)
        if sessionCreate:
            session = sessionCreate()
            ATTR_SQL_SESSION.set(thread, session)
            ATTR_SQL_SESSION_CREATE.delete(thread)
            assert log.debug('Created SQL Alchemy session') or True
    assert session, 'Invalid call, it seems that the thread is not tagged with an SQL session'
    return session

# --------------------------------------------------------------------

def registerSessionCreator(sessionCreator):
    '''
    Register the provided session creator to this thread.
    
    @param sessionCreator: class
        The session creator class.
    '''
    assert issubclass(sessionCreator, Session), 'Invalid session creator %s' % sessionCreator
    ATTR_SQL_SESSION_CREATE.set(current_thread(), sessionCreator)

def open(sessionCreator):
    '''
    Opens a new session on the current thread.
    '''
    assert issubclass(sessionCreator, Session), 'Invalid session creator %s' % sessionCreator
    ATTR_SQL_SESSION_CREATE.set(current_thread(), sessionCreator)

def commit(session=None):
    '''
    Commit the current thread session.
    '''
    session = session or ATTR_SQL_SESSION.get(current_thread(), None)
    if session:
        assert isinstance(session, Session)
        try:
            session.commit()
            assert log.debug('Committed SQL Alchemy session transactions') or True
        except InvalidRequestError:
            assert log.debug('Nothing to commit on SQL Alchemy session') or True
        except Exception as e:
            #TODO: add handling when commit fails
            assert log.debug('Problems committing %r', e) or True
        session.close()
        _clear()
        assert log.debug('Properly closed SQL Alchemy session') or True

def rollback(session=None):
    '''
    Roll back the current thread session.
    '''
    session = session or ATTR_SQL_SESSION.get(current_thread(), None)
    if session:
        session.rollback()
        session.close()
        _clear()
        assert log.debug('Improper SQL Alchemy session, rolled back transactions') or True

# --------------------------------------------------------------------

def _clear():
    '''
    Clears the current thread of any alchemy session info.
    '''
    thread = current_thread()
    if ATTR_SQL_SESSION.has(thread): ATTR_SQL_SESSION.delete(thread)
    if ATTR_SQL_SESSION_CREATE.has(thread): ATTR_SQL_SESSION_CREATE.delete(thread)
