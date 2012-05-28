'''
Created on May 26, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for meta services.
'''

from ally.core.http.impl.meta.parameter import ParameterMetaService
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.entity
def parameterMetaService(): return ParameterMetaService()
