'''
Created on June 14, 2012

@package: support sqlalchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="support_sqlalchemy",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_sqlalchemy >= 1.0',
                      'internationalization >= 1.0'],
    platforms=['all'],
    zip_safe=True,

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Ally framework - SQLAlchemy support plugin",
    long_description='Provides support for generic entity handling.',
    license="GPL v3",
    keywords="Ally REST framework plugin SQLAlchemy",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
