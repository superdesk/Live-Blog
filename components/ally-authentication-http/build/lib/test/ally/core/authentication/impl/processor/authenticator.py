'''
Created on Jul 11, 2012

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides unit testing for the authentication header handling.
'''

# --------------------------------------------------------------------

import unittest
from time import sleep
import hmac
import hashlib
from sys import getdefaultencoding
from collections import deque
from ally.core.authentication.api.authentication import IAuthenticate
from ally.core.authentication.impl.processor.authenticator import AuthenticationHandler
from ally.exception import InputError
from datetime import timedelta

# --------------------------------------------------------------------

class UserKeyGenerator(IAuthenticate):
    def getUserKey(self, _userName):
        return 'user secret key'

class TestHTTPDelivery(unittest.TestCase):
    userName = 'test_user'

    def testAuthenticationHandler(self):
        # initializations
        ah = AuthenticationHandler()
        ah._sessions = {}
        ah._sessionsExpirations = deque()
        ah.userKeyGenerator = UserKeyGenerator()
        ah.resourcesRegister = None

        # Test the login method on expired token
        loginToken = ah.loginToken(self.userName)
        ah.login_token_timeout = timedelta(seconds=0)
        sleep(1)
        try: ah.login(self.userName, loginToken, None)
        except InputError: pass
        else: self.fail('The login token was not cleaned on timeout')

        # Test the login method with invalid token input
        ah.login_token_timeout = timedelta(seconds=10)
        loginToken = ah.loginToken(self.userName)
        try: ah.login(self.userName, loginToken, 'invalid hashed token')
        except InputError: pass
        else: self.fail('The login returned success with invalid hashed token input')

        # Test the login method with valid token input
        loginToken = ah.loginToken(self.userName)
        key = bytes(self.userName + ah.userKeyGenerator.getUserKey(self.userName), getdefaultencoding())
        hashedToken = hmac.new(key, bytes(loginToken, getdefaultencoding()), hashlib.sha512).hexdigest()
        try: ah.login(self.userName, loginToken, hashedToken)
        except InputError: self.fail('The login raised exception on valid login token')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
