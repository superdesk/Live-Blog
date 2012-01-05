'''
Created on Jan 5, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy a processor for automatic session handling.
'''

from ally.container.ioc import injected
from ally.core.spec.server import Processor, Response, ProcessorsChain
from ally.support.sqlalchemy.session import rollback, commit, \
    registerSessionCreator
from sqlalchemy.orm.session import Session

# --------------------------------------------------------------------

@injected
class AlchemySessionHandler(Processor):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling.
    '''
    
    sessionCreator = None
    # The alchemy session used for creating sessions
    
    def __init__(self):
        '''
        Construct the session stuff.
        '''
        assert issubclass(self.sessionCreator, Session), 'Invalid session creator %s' % self.sessionCreator

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        registerSessionCreator(self.sessionCreator)
        try:
            chain.process(req, rsp)
        except:
            rollback()
            raise
        if rsp.code.isSuccess:
            commit()
        else:
            rollback()
