'''
Created on December 20, 2012

@package: url info
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="url_info",
    version="1.0",
    packages=find_packages(),
    install_requires=[],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    },

    # metadata for upload to PyPI
    author="Mugur Rus",
    author_email="mugur.rus@sourcefabric.org",
    description="URL info plugin",
    long_description='Service for retrieving information about an URL (model, service)',
    license="GPL v3",
    keywords="Ally REST framework plugin",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
