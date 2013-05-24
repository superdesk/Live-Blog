'''
Created on April 29, 2013

@package: frontline
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="frontline",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_sqlalchemy >= 1.0', 'ally_core_plugin >= 1.0', 'superdesk >= 1.0'],
    platforms=['all'],
    zip_safe=True,

    # metadata for upload to PyPI
    author="Martin Saturka",
    author_email="martin.saturka@sourcefabric.org",
    description="Superdesk frontline API plugin",
    long_description='Superdesk frontline API plugin',
    license="GPL v3",
    keywords="Ally REST framework plugin Superdesk",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
