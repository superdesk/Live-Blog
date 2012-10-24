'''
Created on June 14, 2012

@package: ally utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name='ally_utilities',
    version='1.0',
    packages=find_packages(),
    platforms=['all'],
    test_suite='test',
    py_modules=['package_extender'],
    zip_safe=True,

    # metadata for upload to PyPI
    author='Gabriel Nistor',
    author_email='gabriel.nistor@sourcefabric.org',
    description='Ally framework - utilities component',
    long_description='The utilities component of the Ally framework',
    license='GPL v3',
    keywords='Ally REST framework',
    url='http://www.sourcefabric.org/en/superdesk/', # project home page
)
