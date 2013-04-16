'''
Created on June 14, 2012

@package: support RBAC
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="security_rbac",
    version="1.0",
    packages=find_packages(),
    install_requires=['security >= 1.0'],
    platforms=['all'],
    zip_safe=True,

    # metadata for upload to PyPI
    author="Ioan v. Pocol",
    author_email="gabriel.nistor@sourcefabric.org",
    description="RBAC structure plugin",
    long_description='RBAC structure',
    license="GPL v3",
    keywords="Ally REST framework support RBAC plugin",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
