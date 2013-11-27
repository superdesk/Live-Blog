'''
Created on Apr 19, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the superdesk source setup files.
'''

# --------------------------------------------------------------------

NAME = 'Sources source'
GROUP = 'Superdesk'
VERSION = '1.0'
DESCRIPTION = 'Provides the support for content sources.'
LONG_DESCRIPTION = 'Source management functionality (model, service)'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'source']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'internationalization >= 1.0',
                    'superdesk >= 1.0']

__extra__  = dict()
