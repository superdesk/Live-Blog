'''
Created on Jul 15, 2011

@package: superdesk security
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Contains the superdesk authentication setup files.
'''

# --------------------------------------------------------------------

NAME = 'Superdesk security'
GROUP = 'Superdesk'
VERSION = '1.0'
DESCRIPTION = 'Provides the the superdesk security'
LONG_DESCRIPTION = 'Authentication services'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'security']
INSTALL_REQUIRES = ['superdesk-user >= 1.0', 'security-rbac >= 1.0' ]

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    })