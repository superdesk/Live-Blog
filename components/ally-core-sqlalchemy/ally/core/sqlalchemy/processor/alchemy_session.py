'''
Created on Jan 5, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy a processor for automatic session handling.
'''

from ally.core.spec.server import Processor, Response, ProcessorsChain
from ally.support.sqlalchemy.session import rollback, commit, ATTR_KEEP_ALIVE, \
    endAll

# --------------------------------------------------------------------

class AlchemySessionHandler(Processor):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling.
    '''

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        ATTR_KEEP_ALIVE.set(True)
        try:
            chain.process(req, rsp)
        except:
            endAll(rollback)
            raise
        if not rsp.code.isSuccess: endAll(rollback)
        ATTR_KEEP_ALIVE.clear()
            
class AlchemySessionCommitHandler(Processor):
    '''
    Implementation for a processor that provides the SQLAlchemy session commit handling, usually the commit handler is
    processed before encoding.
    '''

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if rsp.code.isSuccess: endAll(commit)
        chain.process(req, rsp)
