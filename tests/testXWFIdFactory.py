# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('XWFIdFactory')

testXML = """<?xml version="1.0" ?>
<root>
  <testnode someattribute="foo">
    Some test text.
  </testnode>
  <emptynode anotherattribute="wibble"/>
</root>"""

class FakePOSTRequest:
    """ A really minimal class to fake a POST. Probably looks
    nothing like the real thing, but close enough for our needs :)
    
    """
    import StringIO
    stdin = StringIO.StringIO(testXML)

def minimallyEqualXML(one, two):
    """ Strip all the whitespace out of two pieces of XML code, having first converted
    them to a DOM as a minimal test of equivalence.
    
    """
    from xml.dom import minidom
    
    sf = lambda x: filter(lambda y: y.strip(), x)
    
    onedom = minidom.parseString(one)
    twodom = minidom.parseString(two)
    
    return sf(onedom.toxml()) == sf(twodom.toxml())

from Products.XWFIdFactory import XWFIdFactory
class TestXWFIdFactory(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        self.idfactory = self._setupXWFIdFactory()
        self.idfactory.upgrade()
        self.idfactory.register('http://testname.com')
                        
    def beforeTearDown(self):
        self.idfactory.deregister('http://testname.com')

    def _setupXWFIdFactory(self):
        """ Create a new XWFIdFactory as the basis for our tests.
        
        """
        XWFIdFactory.manage_addXWFIdFactory(self.folder, 'idfactory', None)
        
        return self.folder.idfactory

    def _setupNamespaces(self, namespace='http://testname.com'):
        """ Register a namespace with the ID Factory.
        
        """
	self.idfactory.register(namespace)
        
        return self.idfactory        

    def test_1_createXWFIdFactory(self):
        self.failUnless(self.idfactory)
        
    def test_2_registerNamespace(self):
        idfactory = self._setupNamespaces('http://foo.com')
        counters = idfactory.get_counters()
        
        self.failUnless(counters.has_key('http://foo.com'))

    def test_3_incrementNamespace1(self):
        value = self.idfactory.next('http://testname.com')

        self.failUnless(value == (1,1))

    def test_4_incrementNamespace50(self):
        value = self.idfactory.next('http://testname.com', 50)
        
        self.failUnless(value == (1,50))

    def test_5_setNamespace(self):
        self.idfactory.set('http://testname.com',150)
        counters = self.idfactory.get_counters()
        
        self.failUnless(counters['http://testname.com'] == 150)

if __name__ == '__main__':
    print framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSomeProduct))
        return suite
