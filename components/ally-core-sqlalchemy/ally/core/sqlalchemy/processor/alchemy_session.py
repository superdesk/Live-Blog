'''
Created on Jan 5, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy a processor for automatic session handling.
'''

from ally.core.spec.server import Response
from ally.design.processor import Handler, Chain
from ally.support.sqlalchemy.session import rollback, commit, ATTR_KEEP_ALIVE, \
    endSessions

# --------------------------------------------------------------------

class AlchemySessionHandler(Handler):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling.
    '''

    def process(self, chain, response:Response, **keyargs):
        '''
        Provides the SQL Alchemy session support.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, Response), 'Invalid response %s' % response

        ATTR_KEEP_ALIVE.set(True)
        try:
            chain.process(response=response, **keyargs)
        except:
            endSessions(rollback)
            raise

        if response.code and response.code.isSuccess: endSessions(commit)
        else: endSessions(rollback)
        ATTR_KEEP_ALIVE.clear()
