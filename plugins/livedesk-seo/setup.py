'''
Created on Feb 5, 2014

@package: Livedesk-SEO
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="livedesk-seo",
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
    author="Ioan v. Pocol",
    author_email="ioan.pocol@sourcefabric.org",
    description="Livedesk SEO plugin",
    long_description='Implementation of the Livedesk SEO plugin',
    license="GPL v3",
    keywords="Ally REST framework plugin Livedesk SEO",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
