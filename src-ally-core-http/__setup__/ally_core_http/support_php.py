'''
Created on Jul 3, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides additional configurations for the Zend PHP client.
'''

from ..ally_core.encoder_decoder import contentTypesJSON
from ally import ioc

# --------------------------------------------------------------------

phpZendSupport = ioc.config(lambda:False, 'Provides additional configurations for the Zend PHP client')

@ioc.before(contentTypesJSON)
def updateContentTypesJSON():
    contentTypesJSON()['application/x-www-form-urlencoded'] = 'application/x-www-form-urlencoded'
