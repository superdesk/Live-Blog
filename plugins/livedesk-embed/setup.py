'''
Created on June 14, 2012

@package: Livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="livedesk-embed",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_sqlalchemy >= 1.0', 'gui_action >= 1.0',
                      'gui_core >= 1.0', 'internationalization >= 1.0', 'superdesk_collaborator >= 1.0',
                      'superdesk_language >= 1.0', 'superdesk_person >= 1.0', 'superdesk_post >= 1.0',
                      'superdesk_source >= 1.0', 'superdesk_user >= 1.0', 'livedesk >= 1.0'],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    },

    # metadata for upload to PyPI
    author="Mihai Nistor",
    author_email="mihai.nistor@sourcefabric.org",
    description="Livedesk embed plugin",
    long_description='Implementation of the Livedesk embed plugin',
    license="GPL v3",
    keywords="Ally REST framework plugin Livedesk embed",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
