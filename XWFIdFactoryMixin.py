# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
from AccessControl import getSecurityManager, ClassSecurityInfo

class XWFIdFactoryError(Exception):
    pass

class XWFIdFactoryMixin:
    """ An ID factory for producing globally unique ID's for a given
        namespace.
    
    """
    security = ClassSecurityInfo()
    id_factory = 'IdFactory'
    id_namespace = None
    
    def get_idFactory(self):
        """ Return the local id factory.
            
        """
        idfactory = getattr(self, self.id_factory, None)
        if idfactory:
            return idfactory
        else:
            raise XWFIdFactoryError, 'No such ID factory, %s' % self.id_factory

    def get_nextId(self):
        """ Return the next ID associated with our namespace.
        
        """
        idfactory = self.get_idFactory()
        try:
            id = idfactory.next(self.id_namespace)[0]
        except KeyError:
            idfactory.register(self.id_namespace)
            id = idfactory.next(self.id_namespace)[0]
        
        return id