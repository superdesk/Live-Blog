'''
Created on Oct 24, 2013

@package: frontline
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services for sms sync.
'''

from ally.container import support
from frontline.inlet.core.imp.sms_sync import SmsSyncProcess


# --------------------------------------------------------------------

support.createEntitySetup(SmsSyncProcess)

