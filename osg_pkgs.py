#!/usr/bin/python

import os


def get_osg_list(osg_tag):
    cmd = "osg-koji list-tagged --latest --rpms %s" % osg_tag

    handle = os.popen(cmd)

    nvrs = [ line[:-5] for line in handle if line.endswith(".src\n") ]
    return nvrs
    #return strip_dist_tag(nvrs, 'osg')

