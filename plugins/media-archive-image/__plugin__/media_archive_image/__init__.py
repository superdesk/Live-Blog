'''
Created on Apr 19, 2012

@package: superdesk media archive image
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the setup files for superdesk media archive handling for images.
'''

# --------------------------------------------------------------------

NAME = 'Media archive images'
GROUP = 'Superdesk media archive'
VERSION = '1.0'
DESCRIPTION = 'This plugin handles the images in the media archive.'
LONG_DESCRIPTION = 'Image files management functionality'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'Livedesk', 'media-archive', 'image']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0',
                      'gui-core >= 1.0', 'internationalization >= 1.0']

__extra__  = dict(package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html',
             '*.jar', '*.exe', '*.so*', '*.a*', '*.txt', 'AUTHORS', 'COPYING*', 'README*'],
    })

