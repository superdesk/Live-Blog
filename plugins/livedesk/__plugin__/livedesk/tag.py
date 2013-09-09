'''
Created on September 9, 2013

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Defines tags and tag types.
'''

from ally.container import ioc

@ioc.config
def view_tag_type_key():
    ''' The tag type key used for post visibility '''
    return 'visibility'

@ioc.config
def view_hidden_tag_key():
    ''' The tag key used for setting a post visibility as hidden '''
    return 'hidden'

@ioc.config
def status_tag_type_key():
    ''' The tag type key used for post status '''
    return 'status'

@ioc.config
def status_tag_keys():
    ''' The tag key used for setting a post status '''
    return ['idle', 'working', 'finished']

@ioc.config
def verification_tag_type_key():
    ''' The tag type key used for post verification '''
    return 'verification'

@ioc.config
def verification_tag_keys():
    ''' The tag key used for setting a post verification '''
    return ['unconfirmed', 'confirmed', 'reliable source', 'multiple reports', 'not true']

