# Copyright (C) 2003,2004 IOPEN Technologies Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You MUST follow the rules in http://iopen.net/STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
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
    """ A really minimal class to fake a POST. Probably looks nothing like the
    real thing, but close enough for our needs :)
    
    """
    import StringIO
    stdin = StringIO.StringIO(testXML)

def minimallyEqualXML(one, two):
    """ Strip all the whitespace out of two pieces of XML code, having first
    converted them to a DOM as a minimal test of equivalence.
    
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

    def test_01_createXWFIdFactory(self):
        self.failUnless(self.idfactory)
        
    def test_02_registerNamespace(self):
        idfactory = self._setupNamespaces('http://foo.com')
        counters = idfactory.get_counters()
        
        self.failUnless(counters.has_key('http://foo.com'))

    def test_03_incrementNamespace1(self):
        value = self.idfactory.next('http://testname.com')
        
        self.assertEqual(value, (1,1))

    def test_04_incrementNamespace50(self):
        value = self.idfactory.next('http://testname.com', 50)
        
        self.assertEqual(value, (1,50))

    def test_05_setNamespace(self):
        self.idfactory.set('http://testname.com',150)
        counters = self.idfactory.get_counters()
        
        self.assertEqual(counters['http://testname.com'], 150)

if __name__ == '__main__':
    print framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestXWFIdFactory))
        return suite
