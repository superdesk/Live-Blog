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
    name="livedesk-sync",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_sqlalchemy >= 1.0', 'gui_action >= 1.0',
                      'gui_core >= 1.0', 'internationalization >= 1.0', 'livedesk >= 1.0'],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    },

    # metadata for upload to PyPI
    author="Mugur Rus",
    author_email="mugur.rus@sourcefabric.org",
    description="Livedesk blog sync plugin",
    long_description='Implementation of the Livedesk blog sync plugin',
    license="GPL v3",
    keywords="Ally REST framework plugin Livedesk blog sync",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
