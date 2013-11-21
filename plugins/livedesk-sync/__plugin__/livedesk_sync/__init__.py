'''
Created on May 16, 2013

@package: Livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains livedesk-sync setup files.
'''

# --------------------------------------------------------------------

NAME = 'Livedesk sync'
GROUP = 'Livedesk'
VERSION = '1.0'
DESCRIPTION = 'Livedesk blog sync plugin'
LONG_DESCRIPTION = 'Implementation of the Livedesk blog sync plugin'
AUTHOR = 'Mugur Rus'
AUTHOR_EMAIL = 'mugur.rus@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'blog', 'livedesk', 'sync']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0',
                    'gui-core >= 1.0', 'internationalization >= 1.0', 'livedesk >= 1.0']

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    })