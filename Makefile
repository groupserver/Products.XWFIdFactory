# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
#
TOPDIR := $(shell /bin/pwd)
VERSION := $(shell cat VERSION)
PACKAGENAME = "xwfidfactory"
PACKAGEDIR = "XWFIdFactory"
distclean:
	find . -iname "*.pyc" -o -iname "*.tar.gz" -o -iname "*~" | xargs -r rm -f

disttarball: distclean
	cd $(TOPDIR)/..; \
	tar cvfz $(TOPDIR)/${PACKAGENAME}-$(VERSION).tar.gz ./${PACKAGEDIR}

commit:	distclean
	cvs commit
