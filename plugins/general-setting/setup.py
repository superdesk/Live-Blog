'''
Created on January 27, 2014

@package: general settings
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="general settings",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0'],
    platforms=['all'],
    
    # metadata for upload to PyPI
    author="Ioan v. Pocol",
    author_email="ioan.pocol@sourcefabric.org",
    description="General settings",
    long_description='General settings services that can manage different types of grouped settings',
    license="GPL v3",
    keywords="Ally REST framework plugin general settings",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
