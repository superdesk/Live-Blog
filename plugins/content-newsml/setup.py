'''
Created on March 7, 2013

@package: content newsml
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="content_newsml",
    version="1.0",
    packages=find_packages(),
    install_requires=['content_packager >= 1.0'],
    platforms=['all'],

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    description="Content newsml export plugin",
    long_description='Content newsml export based on packager content',
    license="GPL v3",
    keywords="Ally REST framework plugin content",
    url="http://www.sourcefabric.org/en/superdesk/",  # project home page
)
