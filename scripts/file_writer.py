# coding:utf-8
"""
"""

import os


class FileWriter():
    def __init__(self, root_dir_path, logger):
        self._logger = logger
        self._root_dir = root_dir_path
        if not os.path.isdir(self._root_dir):
            self._logger.info('make dir : %s' % self._root_dir)
            os.makedirs(self._root_dir)

    def write_list(self, l, dir_rpath, file_name):
        path = '%s/%s' % (self._root_dir, dir_rpath)
        if not os.path.isdir(path):
            self._logger.info('make dir : %s' % path)
            os.makedirs(path)
        self._logger.info('writing to %s/%s' % (path, file_name))
        for item in l:
            print >>open('%s/%s' % (path, file_name), 'a'), item

    def write_string(self, string, dir_rpath, file_name):
        path = '%s/%s' % (self._root_dir, dir_rpath)
        if not os.path.isdir(path):
            self._logger.info('make dir : %s' % path)
            os.makedirs(path)
        self._logger.info('writing to %s/%s' % (path, file_name))
        print >>open('%s/%s' % (path, file_name), 'w'), string

