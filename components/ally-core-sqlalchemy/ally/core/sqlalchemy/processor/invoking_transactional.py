'''
Created on Jan 5, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy a processor for automatic session handling.
'''

from ally.core.impl.processor.invoking import InvokingHandler, Request, Response
from ally.design.processor import processor
from ally.support.sqlalchemy.session import rollback, commit, ATTR_KEEP_ALIVE, \
    endSessions

# --------------------------------------------------------------------

class InvokingWithTransactionHandler(InvokingHandler):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling.
    '''

    @processor
    def invoke(self, chain, request:Request, response:Response, **keyargs):
        '''
        Wraps the invoking and all processors after invoking in a transaction.
        @see: InvokingHandler.invoke
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response

        ATTR_KEEP_ALIVE.set(True)
        try:
            if super().invoke(chain, request, response, **keyargs):
                chain.process(request=request, response=response, **keyargs)
                # We process the chain inside the try because we need control over the processing.
        except:
            endSessions(rollback)
            raise

        if Response.code in response and response.code.isSuccess: endSessions(commit)
        else: endSessions(rollback)
