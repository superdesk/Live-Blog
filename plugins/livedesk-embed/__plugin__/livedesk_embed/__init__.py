'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the superdesk media archive setup files.
'''

# --------------------------------------------------------------------

NAME = 'Livedesk embed'
GROUP = 'Livedesk'
VERSION = '1.0'
DESCRIPTION = 'This plugin provides the embed scripts for Livedesk.'
LONG_DESCRIPTION = 'Implementation of the Livedesk embed plugin'
AUTHOR = 'Mihai Nistor'
AUTHOR_EMAIL = 'mihai.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'livedesk', 'embed']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0',
                      'gui-core >= 1.0', 'internationalization >= 1.0', 'superdesk-collaborator >= 1.0',
                      'superdesk-language >= 1.0', 'superdesk-person >= 1.0', 'superdesk-post >= 1.0',
                      'superdesk-source >= 1.0', 'superdesk-user >= 1.0', 'livedesk >= 1.0']

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    })
