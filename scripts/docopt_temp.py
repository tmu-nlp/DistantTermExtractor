# coding:utf-8
u"""
test

Usage:
    test [-c <root_cat> | --category <root_cat>] [-d <depth> | --depth <depth>]
    test -h | --help
    test -v | --version

Option:
     -h, --help
        Show this screen.
     -v, --version
        Show version.
     -c <root_cat>, --category <root_cat>
        ルートカテゴリ名 [default: test]
     -d <depth>, --depth <depth>
        カテゴリの深さ [default: 1]
"""

from docopt import docopt

def test(x):
    if x is None:
        return x
    if isinstance(x,bool):
        return x
    if x.isdigit():
        return int(x)
    if isinstance(x, unicode):
        return x.encode('utf-8')
    return x


args = docopt(__doc__, version='test_version')

for key in args:
    print
    print "key:"+ key
    print "arg:"+ str(test(args[key]))
    print "type:"+ str(type(test(args[key])))
