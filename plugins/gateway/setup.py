'''
Created on June 14, 2012

@package: gateway
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="gateway",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0'],
    platforms=['all'],
    zip_safe=True,

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Ally framework - gateway",
    long_description='The plugin that provides the gateway support',
    license="GPL v3",
    keywords="Ally REST framework plugin gateway",
    url="http://www.sourcefabric.org/en/superdesk/",  # project home page
)
