'''
Created on May 26, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for meta services.
'''

from ally.container import ioc
from ally.core.impl.meta.model import ModelMetaService

# --------------------------------------------------------------------

@ioc.entity
def modelMetaService(): return ModelMetaService()
