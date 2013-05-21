'''
Created on March 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="content_article",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'internationalization >= 1.0', 'gui_action >= 1.0',
                      'gui_core >= 1.0'],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html', '*.xml'],
    },

    # metadata for upload to PyPI
    author="Mugur Rus",
    author_email="mugur.rus@sourcefabric.org",
    description="Content article plugin",
    long_description='Content packager functionality (model, service)',
    license="GPL v3",
    keywords="Ally REST framework plugin article",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
