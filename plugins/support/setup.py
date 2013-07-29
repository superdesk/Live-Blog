'''
Created on March 11, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="support",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0'],
    platforms=['all'],
    
    # metadata for upload to PyPI
    author="Mugur Rus",
    author_email="mugur.rus@sourcefabric.org",
    description="Support services",
    long_description='Support services that can be easlly extended for additional data',
    license="GPL v3",
    keywords="Ally REST framework plugin support",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
