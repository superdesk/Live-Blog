'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for header encoders.
'''

from ally import ioc
from .processor import headerStandard, headerX

# --------------------------------------------------------------------

encodersHeader = ioc.entity(lambda: [headerStandard(), headerX()])
