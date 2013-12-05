'''
Created on Oct 23, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Init the settings related to disable captcha gateway used by comments.
If the captcha is used please comment the below settings
'''
from __plugin__.gateway.service import default_gateways
from ally.container import ioc
from ally.http.spec.server import HTTP_POST

@ioc.config
def captcha_pattern_resources():
    '''
    The pattern used for matching the REST resources paths for captcha
    '''
    return 'resources\/LiveDesk\/Blog\/([0-9\-]+)\/Comment\/Post[\/]?(\.|$)'

@ioc.before(default_gateways)
def updateGatewayWithCaptcha():
        default_gateways().extend([
                                   {
                                    'Pattern': captcha_pattern_resources(),
                                    'Methods': [HTTP_POST],
                                    },
                                   ])