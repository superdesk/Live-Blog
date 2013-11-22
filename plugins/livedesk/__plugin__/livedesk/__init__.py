'''
Created on May 3rd, 2011

@package: Livedesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains livedesk setup files.
'''

# --------------------------------------------------------------------

NAME = 'Livedesk core'
GROUP = 'Livedesk'
VERSION = '1.0'
DESCRIPTION = 'Livedesk plugin'
LONG_DESCRIPTION = 'Implementation of the Livedesk plugin'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', '']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0',
                      'gui-core >= 1.0', 'internationalization >= 1.0', 'superdesk-collaborator >= 1.0',
                      'language >= 1.0', 'superdesk-person >= 1.0', 'superdesk-post >= 1.0',
                      'superdesk-source >= 1.0', 'superdesk-user >= 1.0', 'support >= 1.0']

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html', '*.csv'],
    })
