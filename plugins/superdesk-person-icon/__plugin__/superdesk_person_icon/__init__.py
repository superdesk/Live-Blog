'''
@package: superdesk person icon
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

NAME = 'superdesk person icon'
GROUP = 'superdesk'
VERSION = '1.0'
DESCRIPTION = 'Superdesk person icon plugin'
LONG_DESCRIPTION = 'Person icon management functionality (model, service)'
AUTHOR = 'Mugur Rus'
AUTHOR_EMAIL = 'mugur.rus@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'person', 'icon']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0',
                    'gui-core >= 1.0', 'internationalization >= 1.0', 'superdesk >= 1.0',
                    'superdesk-person >= 1.0']

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    })