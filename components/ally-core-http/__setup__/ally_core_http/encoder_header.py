'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for header encoders.
'''

from .processor import headerStandard, formattingProvider
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.entity
def encodersHeader(): return [headerStandard(), formattingProvider()]
