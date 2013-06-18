'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="superdesk_desk",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_sqlalchemy >= 1.0', 'superdesk >= 1.0',
                      'internationalization >= 1.0', 'superdesk_user >= 1.0', 'support >= 1.0'],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    },

    # metadata for upload to PyPI
    author="Martin Saturka",
    author_email="martin.saturka@sourcefabric.org",
    description="Superdesk desk plugin",
    long_description='Desk management functionality (model, service)',
    license="GPL v3",
    keywords="Ally REST framework plugin Superdesk",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
