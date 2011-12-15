'''
Created on Dec 1, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configuration for the database session handling.
'''

from ally.core.support.sql_alchemy import AlchemySessionHandler
from ally import ioc

# --------------------------------------------------------------------

def alchemySessionHandler(alchemySessionCreator, handlers, invokingHandler) -> AlchemySessionHandler:
    b = AlchemySessionHandler()
    b.sessionCreator = alchemySessionCreator
    return b

# ---------------------------------

@ioc.before('handlers')
def updateHandlers(handlers, invokingHandler, alchemySessionHandler):
    handlers.insert(handlers.index(invokingHandler), alchemySessionHandler)
