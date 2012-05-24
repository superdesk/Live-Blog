'''
Created on Jan 5, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy a processor for automatic session handling.
'''

from ally.core.spec.server import IProcessor, Response, ProcessorsChain
from ally.support.sqlalchemy.session import rollback, commit, ATTR_KEEP_ALIVE, \
    endSessions

# --------------------------------------------------------------------

class AlchemySessionHandler(IProcessor):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling.
    '''

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        ATTR_KEEP_ALIVE.set(True)
        try:
            chain.process(req, rsp)
        except:
            endSessions(rollback)
            raise
        if rsp.code.isSuccess: endSessions(commit)
        else: endSessions(rollback)
        ATTR_KEEP_ALIVE.clear()
