'''
Created on Jul 3, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides additional configurations for the Zend PHP client.
'''

from ally import ioc

# --------------------------------------------------------------------

@ioc.onlyIf(_phpZendSupport=True, doc='Provides additional configurations for the Zend PHP client')
@ioc.before
def updateContentTypesJSON(_contentTypesJSON):
    _contentTypesJSON['application/x-www-form-urlencoded'] = 'application/x-www-form-urlencoded'
