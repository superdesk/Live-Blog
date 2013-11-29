'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides the mongo database settings for content plugins.
'''

from ..mongo_engine.db_application import bindApplicationConnection
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.entity
def binders(): return [bindApplicationConnection]
