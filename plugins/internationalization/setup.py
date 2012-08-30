'''
Created on June 14, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="internationalization",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_plugin >= 1.0', 'ally_core_sqlalchemy >= 1.0',
                      'support_admnistration >= 1.0', 'support_cdm >= 1.0'],
    platforms=['all'],
    test_suite='test',
    zip_safe=True,

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Ally framework - Internationalization plugin",
    long_description='The plugin that implements internationalization support',
    license="GPL v3",
    keywords="Ally REST framework plugin internationalization",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
