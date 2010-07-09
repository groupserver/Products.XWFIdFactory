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
import os

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

from Products.XWFCore.XWFUtils import locateDataDirectory

from App.class_init import InitializeClass
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
    
from threading import Lock

_thread_lock = Lock()

class XWFIdFactory(SimpleItem):
    """ An ID factory for producing globally unique ID's for a given
        namespace.
    
    """
    security = ClassSecurityInfo()
    
    meta_type = 'XWF Id Factory'
    version = 0.11

    manage_options = ({'label': 'Configure',
                       'action': 'manage_main'},
                      )+SimpleItem.manage_options
    
    manage_main = PageTemplateFile('management/main.zpt',
                                    globals(),
                                    __name__='manage_main')

    base_counters_dir = locateDataDirectory("groupserver.XWFIdFactory.counters")
    
    def __init__(self, id, file=None):
        """ Initialise a new instance of XWFIdFactory.
        
            Unittest: TestXWFIdFactory
            
        """
        self.__name__ = id
        self.id = id
        self.init_properties()        
    
    security.declarePrivate('init_properties')
    def init_properties(self):
        """ Initialise the object properties.
            
            Unittest: TestXWFIdFactory
            
        """
        try: self.namespaces
        except AttributeError: self.namespaces = []
    
    security.declarePrivate('init_counters')
    def init_counters(self):
        """ Initialise the object counters.
        
            This must be called _after_ the object is introduced into
            the ZODB, and the object must be retrieved from the ZODB
            first (ie. not called on the original object instance) in
            order to get the correct physical path.
            
            Unittest: TestXWFIdFactory
            
        """
        import shutil
        orig_counters_dir = getattr(self, 'counters_dir', None)
        
        self.counters_dir = os.path.join(self.base_counters_dir,
                                         apply(os.path.join,
                                               self.getPhysicalPath()))
        
        # make sure the base counters directory has been created
        try:
            os.makedirs(self.counters_dir, 0770)
        except OSError, x:
            if x.errno == 17:
                pass
            else:
                raise
    
        # if the orig_counters_dir exists, we are being copied, so we
        # need to copy the counter files as well
        if orig_counters_dir and os.path.exists(orig_counters_dir):
            for counter_file in os.listdir(orig_counters_dir):
                ofile = os.path.join(orig_counters_dir, counter_file)
                nfile = os.path.join(self.counters_dir, counter_file)
                shutil.copy(ofile, nfile)            

    def manage_afterAdd(self, item, container):
        """ For configuring the object post-instantiation.
    
            Note: this gets called both after adding _and_ after copying,
            so take extra care to be sure nothing is initialised here that
            shouldn't be initialised after a copy!
            
            Unittest: TestXWFIdLibrary
             
        """
        try:
            item.init_counters()
        except:
            pass
        
        return 1
        
    security.declareProtected('Upgrade objects', 'upgrade')
    security.setPermissionDefault('Upgrade', ('Manager', 'Owner'))
    def upgrade(self):
        """ Upgrade to the latest version.
            
            Unittest: TestXWFIdFactory
            
        """
        currversion = getattr(self, '_version', 0)
        
        if currversion == self.version:
            return 'already running latest version (%s)' % currversion

        self._version = self.version
        self.init_properties()
        self.init_counters()
        
        return 'upgraded %s to version %s from version %s' % (self.getId(),
                                                              self._version,
                                                              currversion)
    
    def _read_counter(self, namespace):
        """ Read the counter from a file, given the namespace.
            
        """
        nsfn = md5.new(namespace).hexdigest()
        _thread_lock.acquire()
        try:
            f = file('%s/%s' % (self.counters_dir, nsfn))
            value = f.read()
            value.strip()
        finally:
            _thread_lock.release()            

        return int(value)

    def _write_counter(self, namespace, value):
        """ Write the counter to a file, given the namespace.
            
        """
        nsfn = md5.new(namespace).hexdigest()
        _thread_lock.acquire()
        try:
            f = file('%s/%s' % (self.counters_dir, nsfn), 'w+')
            f.write(str(value))
        finally:
            _thread_lock.release()        
        
        return 1

    def _remove_counter(self, namespace):
        """ Remove the counter file, given the namespace.
            
        """
        nsfn = md5.new(namespace).hexdigest()
        _thread_lock.acquire()
        try:
            os.remove('%s/%s' % (self.counters_dir, nsfn))
        finally:
            _thread_lock.release()            
        
        return 1

    security.declareProtected('View', 'register')
    def register(self, namespace):
        """ Register a new namespace with the system.
        
            Unittest: TestXWFIdFactory.test_2_registerNamespace
            
        """
        if namespace in self.namespaces or not namespace:
            return 0
        
        self._write_counter(namespace, 0)
        self.namespaces.append(namespace)
        self.namespaces.sort()
        self._p_changed = 1
        
        return 1

    security.declareProtected('View', 'deregister')
    def deregister(self, namespace):
        """ Deregister a previously registered namespace.
        
            Raises KeyError if the namespace does not exist.
            
            Unittest: TestXWFIdFactory
            
        """
        if namespace not in self.namespaces:
            raise KeyError, 'namespace does not exist'
        self._remove_counter(namespace)
        self.namespaces.remove(namespace)
        self._p_changed = 1
        
        return 1
    
    security.declareProtected('View', 'set')
    def set(self, namespace, value=0):
        """ Set the counter associated with a given namespace.
            
            Optionally takes a value parameter for setting the
            counter to a particular value, which defaults to 0
            (useful for resetting the counter).
            
            Returns 1 on success, Raises KeyError if the namespace
            does not exist.
            
            Unittest: TestXWFIdFactory.test_5_setNamespace
            
        """
        if namespace in self.namespaces:
            _thread_lock.acquire()
            try:
                self._write_counter(namespace, int(value))
                return 1
            finally:
                _thread_lock.release()
           
        raise KeyError, 'namespace does not exist'
    
    security.declareProtected('View', 'next')
    def next(self, namespace, length=1):
        """ Get the next value associated with the namespace.
            
            Optionally takes a length parameter to specify the length
            of the range you wish to receive, for example you may
            want a range protected for offline processing.
            
            Unittest: TestXWFIdFactory.test_3_incrementNamespace1, test_4_incrementNamespace50 
            
        """
        length = int(length)
        
        if namespace not in self.namespaces:
            raise KeyError, 'namespace does not exist'
        
        _thread_lock.acquire()
        try:
            current = self._read_counter(namespace)
            self._write_counter(namespace, current+length)
        finally:
            _thread_lock.release()        
        
        return (current+1, current+length)
    
    security.declareProtected('View', 'get_counters')
    def get_counters(self):
        """ Return the dictionary of all namespaces and counters.
            
            Unittest: TestXWFIdFactory
            
        """
        counters = {}
        for namespace in self.namespaces:
            counters[namespace] = self._read_counter(namespace)
        
        return counters

    ### Zope Management Form Methods ###
    security.declareProtected('View management screens', 'manage_register')
    def manage_register(self, namespaces, REQUEST, RESPONSE):
        """ Register a new namespace.
            
        """
        if type(namespaces) == type(''):
            namespaces = [namespaces]
        for namespace in namespaces:
            if namespace.strip():
                self.register(namespace)

        return RESPONSE.redirect('%s/manage_main' % REQUEST['URL1'])
    
    security.declareProtected('View management screens', 'manage_deregister')
    def manage_deregister(self, namespaces, REQUEST, RESPONSE):
        """ Register a new namespace.
            
        """
        if type(namespaces) == type(''):
            namespaces = [namespaces]
        for namespace in namespaces:
            self.deregister(namespace)
        
        return RESPONSE.redirect('%s/manage_main' % REQUEST['URL1'])

InitializeClass(XWFIdFactory)

#
# Zope Management Methods
#
manage_addXWFIdFactoryForm = PageTemplateFile(
    'management/manage_addXWFIdFactoryForm.zpt',
    globals(), __name__='manage_addXWFIdFactoryForm')

def manage_addXWFIdFactory(self, id,
                           REQUEST=None, RESPONSE=None, submit=None):
    """ Add a new instance of XWFIdFactory.
        
    """
    obj = XWFIdFactory(id)
    self._setObject(id, obj)
    
    obj = getattr(self, id)
    
    if RESPONSE and submit:
        if submit.strip().lower() == 'add':
            RESPONSE.redirect('%s/manage_main' % self.DestinationURL())
        else:
            RESPONSE.redirect('%s/manage_main' % id)

def initialize(context):
    # make sure the base counters directory has been created
    try:
        os.makedirs(XWFIdFactory.base_counters_dir, 0770)
    except OSError, x:
        if x.errno == 17:
            pass
        else:
            raise
    context.registerClass(
        XWFIdFactory,
        permission='Add XWF Id Factory',
        constructors=(manage_addXWFIdFactoryForm,
                      manage_addXWFIdFactory),
        icon='icons/ic-idfactory.png'
        )
