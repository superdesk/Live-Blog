'''
Created on June 14, 2012

@package: Newscoop
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="superdesk_gateway",
    version="1.0",
    packages=find_packages(),
    install_requires=['superdesk_user >= 1.0', 'security_rbac >= 1.0', 'security_http_acl >= 1.0' ],
    platforms=['all'],
    zip_safe=True,
    package_data={
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html'],
    },

    # metadata for upload to PyPI
    author="Gabriel Nistor",
    author_email="gabriel.nistor@sourcefabric.org",
    description="Superdesk authentication plugin",
    long_description='Authentication services',
    license="GPL v3",
    keywords="Ally REST framework plugin gateway",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
