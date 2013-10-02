'''
Created on September 10, 2013

@package: frontline inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Defines SMS types.
'''

from ally.container import ioc

# --------------------------------------------------------------------

@ioc.config
def sms_source_types():
    ''' The source types used during SMS processing '''
    return ['FrontlineSMS']

@ioc.config
def sms_post_types():
    ''' The post types used during SMS processing '''
    return ['normal']
