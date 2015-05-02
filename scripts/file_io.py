# coding:utf-8
"""
"""

import os
import glob

class FileIO():
    def __init__(self, root_dir_path, logger):
        self._logger = logger
        self._root_dir = root_dir_path
        if not os.path.isdir(self._root_dir):
            self._logger.info('make dir : %s' % self._root_dir)
            os.makedirs(self._root_dir)

    def write_list(self, l, dir_rpath, file_name):
        path = self._get_path(dir_rpath)
        if not os.path.isdir(path):
            self._logger.info('make dir : %s' % path)
            os.makedirs(path)
        self._logger.info('writing to %s/%s' % (path, file_name))
        for item in l:
            print >>open('%s/%s' % (path, file_name), 'a'), item

    def write_string(self, string, dir_rpath, file_name):
        path = self._get_path(dir_rpath)

        if not os.path.isdir(path):
            self._logger.info('make dir : %s' % path)
            os.makedirs(path)
        self._logger.info('writing to %s/%s' % (path, file_name))
        print >>open('%s/%s' % (path, file_name), 'w'), string

    def rewrite_files(self, read_rpath, write_rpath, rewrite_func):
        u"""
        ディレクトリ内のファイルを書き換えて別のディレクトリに出力する.

        @parm read_rpath    読み込むディレクトリの相対パス
        @parm write_rpath   書き込むディレクトリの相対パス
        @parm rewrite_func  読み込みと書き込みのファイルオブジェクトを受け取って書き換え操作を行う関数
        """
        rpath = self._get_path(read_rpath)
        wpath = self._get_path(write_rpath)

        if not os.path.isdir(wpath):
            self._logger.info('make dir : %s' % wpath)
            os.makedirs(wpath)

        for f in self._pyls(rpath, False, False):
            wf = open('%s/%s' % (wpath, f), 'w')
            rf = open('%s/%s' % (rpath, f))
            rewrite_func(wf, rf)
            wf.close()
            rf.close()

    def _get_path(self, rpath):
        return '%s/%s' % (self._root_dir, rpath)

    def _pyls(self, query, enable_dir=True, enable_path=False):
        u"""
        lsの結果を返すジェネレータ.
    
        @parm query         ディレクトリのパスとかワイルドカードとか
        @parm enable_dir    サブディレクトリを含めるかどうか(デフォルトはTrue)
        @parm enable_path   パスを含めて返すかどうか（デフォルトはFalse）
        @yield ファイル名
        """
        for f in glob.glob(query):
            if not enable_dir:
                if os.path.isdir(f):
                    continue
            if enable_path:
                yield f
            else:
                yield os.path.basename(f)