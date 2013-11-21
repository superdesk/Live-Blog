'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the superdesk media archive setup files.
'''

# --------------------------------------------------------------------

NAME = 'Media archive'
GROUP = 'Superdesk media archive'
VERSION = '1.0'
DESCRIPTION = 'Media files management functionality' 
LONG_DESCRIPTION = 'This plugin provides the support required for other media archive plugins to publish specific media resources.'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'Livedesk', 'media-archive']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0',
                    'gui-core >= 1.0', 'internationalization >= 1.0']

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html', '*.txt', '*.xsd',
             '*.ffpreset', '*.exe'],
    })
