'''
Created on April 29, 2013

@package: frontline
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains frontline setup files.
'''

# --------------------------------------------------------------------

NAME = 'Frontline core'
GROUP = 'FrontlineSMS'
VERSION = '1.0'
DESCRIPTION = 'Provides the the Frontline setups and database configurations'

NAME = 'Frontline core'
GROUP = 'FrontlineSMS'
VERSION = '1.0'
DESCRIPTION = 'Superdesk frontline API plugin'
LONG_DESCRIPTION = 'Superdesk frontline API plugin'
AUTHOR = 'Martin Saturka'
AUTHOR_EMAIL = 'martin.saturka@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'Frontline']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'ally-plugin >= 1.0', 'superdesk >= 1.0']

__extra__  = dict()