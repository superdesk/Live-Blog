'''
Created on June 14, 2012

@package: GUI core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="gui_core",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'ally_core_plugin >= 1.0', 'support_cdm >= 1.0'],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    },

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Ally framework - GUI core plugin",
    long_description='The plugin that contains the core GUI resources',
    license="GPL v3",
    keywords="Ally REST framework plugin GUI",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
