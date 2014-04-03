'''
Created on April 1, 2014

@package: support testing
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="support_testing",
    version="0.1",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_sqlalchemy >= 1.0',
                      'internationalization >= 1.0'],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.sql'],
    },

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Ally framework - testing support plugin",
    long_description='Provides support for server database reset.',
    license="GPL v3",
    keywords="Ally REST framework plugin testing",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
