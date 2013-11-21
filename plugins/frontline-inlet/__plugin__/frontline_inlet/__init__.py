'''
Created on April 24, 2013

@package: frontline inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the frontline inlet setup files.
'''

# --------------------------------------------------------------------

NAME = 'Frontline inlet SMS support'
GROUP = 'FrontlineSMS'
VERSION = '1.0'
DESCRIPTION = 'Provides the support for frontline-inlet sms.'
LONG_DESCRIPTION = 'Frontline SMS inlet management functionality (model, service)'
AUTHOR = 'Martin Saturka'
AUTHOR_EMAIL = 'martin.saturka@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', '']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'superdesk >= 1.0',
                      'superdesk-collaborator >= 1.0', 'superdesk-post >= 1.0', 'superdesk-source >= 1.0',
                      'superdesk-user >= 1.0', 'frontline >= 1.0', 'internationalization >= 1.0']

__extra__  = dict()