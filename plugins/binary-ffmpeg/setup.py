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
    name='binary_ffmpeg',
    version='1.0',
    packages=find_packages(),
    install_requires=[],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.exe', '*.txt', '*.xsd', '*.ffpreset', '*.so.*'],
    },

    # metadata for upload to PyPI
    author='FFMpeg team',
    author_email='ffmpeg-user@ffmpeg.org',
    description='FFMpeg tool',
    long_description='FFMpeg tool',
    license='GPL v3',
    keywords='Ally REST framework plugin FFMpeg',
    url='http://www.sourcefabric.org/en/superdesk/', # project home page
)
