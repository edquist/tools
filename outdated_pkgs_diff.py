#!/usr/bin/python

import re
import rpm
import sys

try:
    from rpmUtils.miscutils import stringToVersion
except ImportError:
    from miscutils import stringToVersion


class Options:
    use_color  = sys.stdout.isatty()
    show_all   = False
    html_out   = False
    preamble   = None


def strip_dist_tag(seq, dist_pfx):
    if dist_pfx is None:
        return seq
    pat = r'\.%s[^-]*$' % dist_pfx
    return [ re.sub(pat, '', nvr) for nvr in seq ]


def rpmvercmp(a,b):
    return rpm.labelCompare(*[stringToVersion(x) for x in (a,b)])


def n_vr(nvr):
    n,v,r = nvr.rsplit("-",2)
    return n, v+'-'+r


def nvrmap(seq):
    return dict( n_vr(nvr) for nvr in seq )


def colorize_ansi(color, *seq):
    return [ "\x1b[%sm%s\x1b[0m" % (color, x) for x in seq ]


def colorize_html(color, *seq):
    return [ '<span class="%s">%s</span>' % (color, x) for x in seq ]


def colorize_vrx(vr1, vr2, colorizer, vdiff, rdiff):
    v1,r1 = vr1.split('-')
    v2,r2 = vr2.split('-')

    if v1 != v2:
        v1,v2 = colorizer(vdiff, v1, v2)
    elif r1 != r2:
        r1,r2 = colorizer(rdiff, r1, r2)

    return map('-'.join, [[v1,r1],[v2,r2]])


def colorize_ansi_vr(vr1, vr2):
    return colorize_vrx(vr1, vr2, colorize_ansi, '1;32', '1;34')


def colorize_html_vr(vr1, vr2):
    return colorize_vrx(vr1, vr2, colorize_html, 'vdiff', 'rdiff')


def print_header(ops):
    if ops.html_out:
        print ("<html>\n<head>\n<style type='text/css'>\n.vdiff {color:green}\n"
               ".rdiff {color:blue}\n</style>\n</head>\n<body>\n<pre>")

    if ops.preamble:
        print ops.preamble
        print


def get_pkg_diffs(downstream_map, upstream_map, ops):
    pkg_diffs = []
    for pkg in sorted(set(downstream_map) & set(upstream_map)):
        vrcmp = rpmvercmp(downstream_map[pkg], upstream_map[pkg])
        if vrcmp < 0 or ops.show_all:
            pkg_diffs.append([pkg, downstream_map[pkg], upstream_map[pkg]])
    return pkg_diffs


def print_pkg_diffs(pkg_diffs, downstream_label, upstream_label, ops):
    colorize_vr = colorize_html_vr if ops.html_out else colorize_ansi_vr

    if pkg_diffs:  # XXX: modifies pkg_diffs
        pkg_diffs[:0] = [["Package", downstream_label, upstream_label]]
        widths = [ max(map(len,col)) for col in zip(*pkg_diffs) ]
        pkg_diffs[1:1] = [[ '-' * n for n in widths ]]
        for i,row in enumerate(pkg_diffs):
            spacing = [ w-len(x) for x,w in zip(row,widths) ]
            if ops.use_color and i > 1:
                row[1:] = colorize_vr(*row[1:])
            print '  '.join( r + ' ' * s for r,s in zip(row,spacing) ).rstrip()
    else:
        print "No package version differences"


def print_footer(ops):
    if ops.html_out:
        print "</pre>\n</body>\n</html>"


def main(downstream, upstream, ops):
    downstream_list, downstream_label, downstream_dist_pfx = downstream
    upstream_list,   upstream_label,   upstream_dist_pfx   = upstream

    downstream_list = strip_dist_tag(downstream_list, downstream_dist_pfx)
    upstream_list   = strip_dist_tag(upstream_list, upstream_dist_pfx)
    downstream_map  = nvrmap(downstream_list)
    upstream_map    = nvrmap(upstream_list)
    pkg_diffs       = get_pkg_diffs(downstream_map, upstream_map, ops)

    print_header(ops)
    print_pkg_diffs(pkg_diffs, downstream_label, upstream_label, ops)
    print_footer(ops)


if __name__ == '__main__':
    print "This is not a script."

