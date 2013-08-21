'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services for livedesk sync.
'''

from ally.container import support
from livedesk.core.impl.blog_sync import BlogSyncProcess
from livedesk.core.impl.icon_content import ChainedIconContent

# --------------------------------------------------------------------

support.createEntitySetup(BlogSyncProcess)
support.createEntitySetup(ChainedIconContent)
