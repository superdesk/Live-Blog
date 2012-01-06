'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ..ally_core.processor import handlers, invokingHandler, encoding
from ally.container import ioc
from ally.core.spec.server import Processor
from ally.core.sqlalchemy.processor.alchemy_session import AlchemySessionHandler, \
    AlchemySessionCommitHandler

# --------------------------------------------------------------------
# Creating the processors used in handling the sql alchemy session

@ioc.entity
def alchemySessionHandler() -> Processor: return AlchemySessionHandler()

@ioc.entity
def alchemySessionCommitHandler() -> Processor: return AlchemySessionCommitHandler()

# ---------------------------------

@ioc.before(handlers)
def updateHandlers():
    handlers().insert(handlers().index(invokingHandler()), alchemySessionHandler())
    handlers().insert(handlers().index(encoding()), alchemySessionCommitHandler())
