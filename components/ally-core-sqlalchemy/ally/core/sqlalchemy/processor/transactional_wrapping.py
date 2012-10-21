'''
Created on Jan 5, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy a processor for automatic session handling.
'''

from ally.design.processor import Chain, HandlerProcessor
from ally.support.sqlalchemy.session import rollback, commit, setKeepAlive, \
    endSessions
from ally.design.context import Context, optional
from ally.core.spec.codes import Code

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Optional
    code = optional(Code)

# --------------------------------------------------------------------

class TransactionWrappingHandler(HandlerProcessor):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling.
    '''

    def process(self, chain, response:Response, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Wraps the invoking and all processors after invoking in a transaction.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, Response), 'Invalid response %s' % response

        setKeepAlive(True)
        try:
            chain.process(response=response, **keyargs)
            # We process the chain inside the try because we need control over the processing.
        except:
            endSessions(rollback)
            raise

        if Response.code in response and response.code.isSuccess: endSessions(commit)
        else: endSessions(rollback)
