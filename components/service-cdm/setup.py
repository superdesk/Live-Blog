'''
Created on June 14, 2012

@package: service cdm
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name='service_cdm',
    version='1.0',
    packages=find_packages(),
    install_requires=['ally_http >= 1.0'],
    platforms=['all'],
    test_suite='test',
    zip_safe=True,
    package_data={
        '': ['*.zip'],
    },

    # metadata for upload to PyPI
    author='Mugur Rus, Gabriel Nistor',
    author_email='mugur.rus@sourcefabric.org, gabriel.nistor@sourcefabric.org',
    description='Ally framework - Content Delivery Manager component',
    long_description='The Content Delivery Manager component of the Ally framework',
    license='GPL v3',
    keywords='Ally REST framework',
    url='http://www.sourcefabric.org/en/superdesk/', # project home page
)
