'''
Created on June 14, 2012

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="support_acl",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0'],
    platforms=['all'],
    zip_safe=True,

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Support for acl",
    long_description='Support for acl definitions',
    license="GPL v3",
    keywords="Ally REST framework support acl plugin",
    url="http://www.sourcefabric.org/en/superdesk/",  # project home page
)
