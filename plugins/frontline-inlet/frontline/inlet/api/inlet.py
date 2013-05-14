'''
Created on April 24, 2013

@package: frontline inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for frontline sms inlet types.
'''

from ally.support.api.keyed import Entity
from frontline.api.domain_sms import modelSMS

# --------------------------------------------------------------------

@modelSMS
class Inlet(Entity):
    '''
    Provides the frontline sms inlet type model.
    '''

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------
