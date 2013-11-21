'''
Created on Apr 19, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the superdesk posts setup files.
'''

# --------------------------------------------------------------------

NAME = 'superdesk post'
GROUP = 'Superdesk'
VERSION = '1.0'
DESCRIPTION = 'This plugin provides the support for posts messages.'
LONG_DESCRIPTION = 'Post management functionality (model, service)'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'post']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'internationalization >= 1.0',
                    'superdesk >= 1.0', 'superdesk-collaborator >= 1.0', 'superdesk-source >= 1.0',
                    'superdesk-user >= 1.0']

__extra__  = dict()
