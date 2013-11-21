'''
Created on Jul 15, 2011

@package: Superdesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains superdesk setup files.
'''

# --------------------------------------------------------------------

NAME = 'Superdesk core'
GROUP = 'Superdesk'
VERSION = '1.0'
DESCRIPTION = 'Superdesk API plugin'
LONG_DESCRIPTION = 'Provides the the Superdesk setups and database configurations'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'ally-plugin >= 1.0']

__extra__  = dict()