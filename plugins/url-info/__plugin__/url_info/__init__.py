'''
Created on December 20, 2012

@package: url info
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the setup files.
'''

NAME = 'url_info'
VERSION = '1.0'
DESCRIPTION = 'URL info plugin'
LONG_DESCRIPTION = 'Service for retrieving information about an URL (model, service)'
AUTHOR = 'Mugur Rus'
AUTHOR_EMAIL = 'mugur.rus@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'url info']
INSTALL_REQUIRES = []

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    })