# coding:utf-8
u"""
"""

import subprocess


class MorphemeTagger():
    def __init__(self, logger, root):
        self._logger = logger
        self._root = root

    def parse(self, outfile, infile):
        cmd = 'mecab -d %s/my_unidic -Omyform < "%s" > "%s"' % (self._root, infile, outfile)
        self._logger.info('exec mecab: %s' % cmd)
        subprocess.call(cmd, shell=True)
