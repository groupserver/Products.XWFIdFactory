# -*- mode: python; py-indent-offset: 4 -*-
import os, Globals

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from AccessControl import getSecurityManager, ClassSecurityInfo
from Globals import InitializeClass, PersistentMapping
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

import ThreadLock, Globals, md5

_thread_lock = ThreadLock.allocate_lock()

class XWFIdFactory(SimpleItem, PropertyManager):
    """ An ID factory for producing globally unique ID's for a given namespace.

    """
    security = ClassSecurityInfo()

    meta_type = 'XWF Id Factory'
    version = 0.1

    manage_options = ({'label': 'Configure',
                       'action': 'manage_main'},)+SimpleItem.manage_options
    
    manage_main = PageTemplateFile('management/main.zpt',
                                    globals(),
                                    __name__='manage_main')

    counters_dir = os.path.join(Globals.package_home(globals()), 'counters')

    def __init__(self, id, file=None):
        """ Initialise a new instance of XWFIdFactory.

        """
        self.__name__ = id
        self.id = id
        self.init_properties()        

    def init_properties(self):
        """ Initialise the object properties.

        """
        try: self.namespaces
        except AttributeError: self.namespaces = []
        
    def upgrade(self):
        """ Upgrade to the latest version.

        """
        currversion = getattr(self, '_version', 0)
        if currversion == self.version:
            return 'already running latest version (%s)' % currversion

        self._version = self.version
        self.init_properties()
        
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
        import os
        nsfn = md5.new(namespace).hexdigest()
        _thread_lock.acquire()
        try:
            os.remove('%s/%s' % (self.counters_dir, nsfn))
        finally:
            _thread_lock.release()            

        return 1    

    def register(self, namespace):
        """ Register a new namespace with the system.

        """
        if namespace in self.namespaces or not namespace:
            return 0
        
        self._write_counter(namespace, 0)
        self.namespaces.append(namespace)
        self.namespaces.sort()
        self._p_changed = 1
        
        return 1

    def deregister(self, namespace):
        """ Deregister a previously registered namespace.
        
            Raises KeyError if the namespace does not exist.
                
        """
        self._remove_counter(namespace)
        self.namespaces.remove(namespace)
        self._p_changed = 1
        
        return 1
        
    def set(self, namespace, value=0):
        """ Set the counter associated with a given namespace.
            
            Optionally takes a value parameter for setting the
            counter to a particular value, which defaults to 0
            (useful for resetting the counter).

            Returns 1 on success, Raises KeyError if the namespace
            does not exist.

        """
        if namespace in self.namespaces:
            _thread_lock.acquire()
            try:
                self._write_counter(namespace, int(value))
                return 1
            finally:
                _thread_lock.release()
        
        raise KeyError
        
    def next(self, namespace, length=1):
        """ Get the next value associated with the namespace.
            

            Optionally takes a length parameter to specify the length
            of the range you wish to receive, for example you may
            want a range protected for offline processing.
            
        """
        length = int(length)
        
        _thread_lock.acquire()
        try:
            current = self._read_counter(namespace)
            self._write_counter(namespace, current+length)
        finally:
            _thread_lock.release()        

        return (current+1, current+length)

    def get_counters(self):
        """ Return the dictionary of all namespaces and counters.
        
        """
        counters = {}
        for namespace in self.namespaces:
            counters[namespace] = self._read_counter(namespace)
        
        return counters

    ### Zope Management Form Methods ###
    def manage_register(self, namespaces, REQUEST, RESPONSE):
        """ Register a new namespace.

        """
        if type(namespaces) == type(''):
            namespaces = [namespaces]
        for namespace in namespaces:
            if namespace.strip():
                self.register(namespace)

        return RESPONSE.redirect('%s/manage_main' % REQUEST['URL1'])

    def manage_deregister(self, namespaces, REQUEST, RESPONSE):
        """ Register a new namespace.

        """
        if type(namespaces) == type(''):
            namespaces = [namespaces]
        for namespace in namespaces:
            self.deregister(namespace)

        return RESPONSE.redirect('%s/manage_main' % REQUEST['URL1'])

#
# Zope Management Methods
#
manage_addXWFIdFactoryForm = PageTemplateFile(
    'management/manage_addXWFIdFactoryForm.zpt',
    globals(), __name__='manage_addXWFIdFactoryForm')

def manage_addXWFIdFactory(self, id, REQUEST=None, RESPONSE=None, submit=None):
    """ Add a new instance of XWFIdFactory.
        
    """
    obj = XWFIdFactory(id)
    self._setObject(id, obj)
    
    if RESPONSE and submit:
        if submit.strip().lower() == 'add':
            RESPONSE.redirect('%s/manage_main' % self.DestinationURL())
        else:
            RESPONSE.redirect('%s/manage_main' % id)

def initialize(context):
    context.registerClass(
        XWFIdFactory,
        permission='Add XWF Id Factory',
        constructors=(manage_addXWFIdFactoryForm,
                      manage_addXWFIdFactory),
        icon='icons/ic-xml.gif'
        )
