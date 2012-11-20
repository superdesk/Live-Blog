'''
Created on June 14, 2012

@package: superdesk collaborator
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="superdesk_collaborator",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_sqlalchemy >= 1.0', 'superdesk >= 1.0',
                      'superdesk_person >= 1.0', 'superdesk_source >= 1.0'],
    platforms=['all'],
    zip_safe=True,

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Superdesk management collaborator plugin",
    long_description='Collaborator functionality (model, service)',
    license="GPL v3",
    keywords="Ally REST framework plugin Livedesk",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
