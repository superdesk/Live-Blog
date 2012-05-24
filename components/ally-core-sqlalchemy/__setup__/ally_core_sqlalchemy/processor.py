'''
Created on Nov 24, 2011

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ..ally_core.processor import handlersResources, invokingHandler, handlersRedirect
from ally.container import ioc
from ally.core.spec.server import IProcessor
from ally.core.sqlalchemy.processor.alchemy_session import AlchemySessionHandler

# --------------------------------------------------------------------
# Creating the processors used in handling the sql alchemy session

@ioc.entity
def alchemySessionHandler() -> IProcessor: return AlchemySessionHandler()

# --------------------------------------------------------------------

@ioc.before(handlersResources)
def updateHandlersResources():
    handlersResources().insert(handlersResources().index(invokingHandler()), alchemySessionHandler())

@ioc.before(handlersRedirect)
def updateHandlersRedirect():
    handlersRedirect().insert(handlersRedirect().index(invokingHandler()), alchemySessionHandler())
