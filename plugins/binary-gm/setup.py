'''
Created on Sep 14, 2012

@package: media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name='binary_gm',
    version='1.0',
    packages=find_packages(),
    install_requires=[],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.exe', '*.dll', '*.so.*', '*.txt', '*.html', '*.dylib'],
    },

    # metadata for upload to PyPI
    author='GraphicsMagic team',
    author_email='ahuggel@gmx.net',
    description='GraphicsMagic tool',
    long_description='GraphicsMagic tool',
    license='GPL v3',
    keywords='Ally REST framework plugin GM',
    url='http://www.sourcefabric.org/en/superdesk/',  # project home page
)
