'''
@package: superdesk person
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

# --------------------------------------------------------------------

NAME = 'Superdesk person'
GROUP = 'Superdesk'
VERSION = '1.0'
DESCRIPTION = 'Superdesk person plugin'
LONG_DESCRIPTION = 'Person management functionality (model, service)'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'person']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0',
                    'gui-core >= 1.0', 'superdesk >= 1.0', 'superdesk-user >= 1.0']

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    })