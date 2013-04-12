'''
Created on June 14, 2012

@package: GUI actions
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="gui_action",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0'],
    platforms=['all'],
    zip_safe=True,

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Ally framework - GUI actions plugin",
    long_description='The plugin that implements that actions management service',
    license="GPL v3",
    keywords="Ally REST framework plugin GUI",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
