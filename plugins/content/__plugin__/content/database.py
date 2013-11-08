'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides the database settings for content plugins.
'''

from ..sql_alchemy.db_application import metas, bindApplicationSession
from ally.container import ioc
from content.base.meta.metadata_content import meta

# --------------------------------------------------------------------

@ioc.entity
def binders(): return [bindApplicationSession]

# --------------------------------------------------------------------

@ioc.before(metas)
def updateMetasForSuperdesk(): metas().append(meta)
