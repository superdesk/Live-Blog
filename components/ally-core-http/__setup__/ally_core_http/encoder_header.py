'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for header encoders.
'''

from .processor import headerStandard, headerX
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.entity
def encodersHeader(): return [headerStandard(), headerX()]
