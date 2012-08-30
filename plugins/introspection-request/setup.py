'''
Created on June 14, 2012

@package: introspection request
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="introspection_request",
    version="1.0",
    packages=find_packages(),
    install_requires=['ally_api >= 1.0', 'gui_action >= 1.0', 'gui_core >= 1.0',
                      'internationalization >= 1.0'],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    },

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Ally framework - Introspection GUI plugin",
    long_description='Contains the resources for introspection GUI',
    license="GPL v3",
    keywords="Ally REST framework plugin introspection",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
