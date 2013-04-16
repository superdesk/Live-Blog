'''
Created on Nov 24, 2011

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ..ally_core.processor import invoking
from ..ally_core_http.processor import assemblyResources, \
    updateAssemblyResources
from ally.container import ioc
from ally.core.sqlalchemy.processor.transactional_wrapping import \
    TransactionWrappingHandler
from ally.design.processor.handler import Handler

# --------------------------------------------------------------------
# Creating the processors used in handling the sql alchemy session

@ioc.entity
def transactionWrapping() -> Handler: return TransactionWrappingHandler()

# --------------------------------------------------------------------

@ioc.after(updateAssemblyResources)
def updateAssemblyResourcesForAlchemy():
    assemblyResources().add(transactionWrapping(), before=invoking())
