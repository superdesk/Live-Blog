'''
Created on Jan 5, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for SQL alchemy a processor for automatic session handling.
'''

from ally.design.processor.attribute import optional
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor
from ally.support.sqlalchemy.session import rollback, commit, setKeepAlive, \
    endSessions

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Optional
    isSuccess = optional(bool)

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
        
        def onFinalize():
            '''
            Handle the finalization
            '''
            if Response.isSuccess in response:
                if response.isSuccess is True: endSessions(commit)
                else: endSessions(rollback)
            else: endSessions(commit) # Commit if there is no success flag

        def onError():
            '''
            Handle the error.
            '''
            endSessions(rollback)
        
        chain.callBack(onFinalize)
        chain.callBackError(onError)
