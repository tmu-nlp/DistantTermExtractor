# coding:utf-8
u"""
"""

import subprocess


class MorphemeTagger():
    def __init__(self):
        pass

    def parse(self, infile, outfile):
        cmd = 'mecab -d ../my_unidic -Omyform < %s > %s' % (infile, outfile)
        subprocess.call(cmd, shell=True)
