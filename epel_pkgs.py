#!/usr/bin/python

import re
import urllib2


def extract_href_rpm(line, el):
    m = re.search(r'<a href="([^"]+(-[^-"]+){2})\.src\.rpm"', line)
    if m:
        return m.groups()[0]
    m = re.search(r'<a href="(\w)/"', line)
    if m:
        return get_epel_list(el, m.groups()[0])


def get_epel_list(el, subdir=None):
    epel_url = "http://dl.fedoraproject.org/pub/epel/%s/SRPMS/Packages/" % el
    if subdir is not None:
        epel_url += "%s/" % subdir

    handle = urllib2.urlopen(epel_url)

    nvrs = filter(None, [ extract_href_rpm(line, el) for line in handle ])
    if nvrs and type(nvrs[0]) is list:
        nvrs = [ nvr for nvrlist in nvrs for nvr in nvrlist ]
    return nvrs

