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
from AccessControl import ClassSecurityInfo

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
