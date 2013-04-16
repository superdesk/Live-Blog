'''
Created on May 29, 2011

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the proxy module.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.container.impl.proxy import ProxyFilter, createProxy, ProxyWrapper, \
    registerProxyHandler
import unittest

# --------------------------------------------------------------------

class A:

    def methodA(self):
        return 'A.methodA'

class B(A):

    def methodA(self):
        return 'B.methodA'

    def methodB(self):
        return 'B.methodB'

# --------------------------------------------------------------------

class TestProxy(unittest.TestCase):

    def testWrapperProxy(self):
        BProxy = createProxy(B)

        self.assertTrue(BProxy is createProxy(B))

        a_proxy = BProxy(ProxyWrapper(A()))
        b_proxy = BProxy(ProxyWrapper(B()))

        self.assertTrue(isinstance(a_proxy, B))
        self.assertTrue(isinstance(b_proxy, B))

        assert isinstance(a_proxy, B)
        self.assertTrue(a_proxy.methodA is a_proxy.methodA)
        self.assertTrue(a_proxy.methodA() == 'A.methodA')
        self.assertRaises(AttributeError, a_proxy.methodB)

        assert isinstance(b_proxy, B)
        self.assertTrue(b_proxy.methodA is b_proxy.methodA)
        self.assertFalse(a_proxy.methodA is b_proxy.methodA)
        self.assertTrue(b_proxy.methodA() == 'B.methodA')
        self.assertTrue(b_proxy.methodB() == 'B.methodB')

    def testFilterProxy(self):
        BProxy = createProxy(B)

        proxy = BProxy(ProxyFilter(ProxyWrapper(B()), 'methodB'))

        self.assertTrue(isinstance(proxy, B))

        assert isinstance(proxy, B)
        self.assertRaises(AttributeError, proxy.methodA)
        self.assertTrue(proxy.methodB() == 'B.methodB')

    def testProxyRegister(self):
        BProxy = createProxy(B)

        proxy = BProxy(ProxyWrapper(B()))
        registerProxyHandler(ProxyWrapper(A()), proxy.methodA)

        self.assertTrue(isinstance(proxy, B))

        assert isinstance(proxy, B)
        self.assertTrue(proxy.methodA() == 'A.methodA')
        self.assertTrue(proxy.methodB() == 'B.methodB')

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()
