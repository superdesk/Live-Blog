'''
Created on Aug 23, 2012

@package: superdesk media archive video
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="media_archive_video",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_sqlalchemy >= 1.0', 'support_cdm >= 1.0',
                      'internationalization >= 1.0', 'superdesk >= 1.0', 'media_archive >= 1.0'],
    platforms=['all'],
    zip_safe=True,

    # metadata for upload to PyPI
    author="Ioan v. Pocol",
    author_email="ioan.pocol@sourcefabric.org",
    description="Video media archive plugin",
    long_description='Implementation of the video media archive plugin',
    license="GPL v3",
    keywords="Ally REST framework plugin Livedesk",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
