# coding:utf-8
u"""
"""

import subprocess


class MorphemeTagger():
    def __init__(self, logger):
        self._logger = logger

    def parse(self, infile, outfile):
        cmd = 'mecab -d ../my_unidic -Omyform < %s > %s' % (infile, outfile)
        self._logger.info('exec mecab: %s' % cmd)
        subprocess.call(cmd, shell=True)
