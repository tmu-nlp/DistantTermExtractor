# coding:utf-8
u"""
Distant Supervision による用語抽出を行います。

Usage:
    test (-c <root_cat> | --category <root_cat>) [-d <depth> | --depth <depth>] [-o <output_dir> | --output <output_dir>] [-l <log_file> | --log <log_file>]
    test -h | --help
    test -v | --version

Option:
     -h, --help
        Show this screen.
     -v, --version
        Show version.
     -c <root_cat>, --category <root_cat>
        ルートカテゴリ名
     -d <depth>, --depth <depth>
        カテゴリの深さ [default: 1]
     -o <output_dir>, --output <output_dir>
        取得したシードや記事本文，抽出した用語を出力するディレクトリ [default: root/data]
     -l <log_file>, --log <log_file> [dafault:]
        ログ出力先ファイル
"""

from docopt import docopt
import os
from distant_extractor import DistantExtractor

__author__ = "ryosukee"
__version__ = "0.0.0"
__date__ = "2015/03/23"


class Main():

    u"""
    seedとunlabeledデータが渡された時に勝手にラベルをつけて学習するようにする
    wikipedia周りは別にやらせる
    """

    def __init__(self, args):
        # init instance
        self._distant_ex = DistantExtractor(
            args['--category'],
            args['--depth'],
            args['--log'],
            args['--output'],
            args['root']
        )

    def extract(self):

        # TODO: if you get from wikipedia
        # このへんはオプション引数とのかねあいも考える
        # get seed
        self._distant_ex.extract_seed()
        # get unlabeled data
        self._distant_ex.extract_unlabeled_data()

        # pre_prosess
        # cleaning
#        self._distant_ex.cleaning()
#        # morpheme analysis
#        self._distant_ex.morpheme_tagging()
#        # add feature
#        self._distant_ex.add_feature()
#        # labeling
#        self._distant_ex.labeling()
 
        # train by crfpp
        self._distant_ex.train()
        # decode
        # extract fp
        # filtering
        # output


def get_args(dopt):
    args = dict()
    args['root'] = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])  # noqa
    for key in dopt:
        x = dopt[key]
        if dopt[key] is None:
            args[key] = x
        elif isinstance(x, bool):
            args[key] = x
        elif x.isdigit():
            args[key] = int(x)
        elif isinstance(x, unicode):
            args[key] = x.encode('utf-8')
        else:
            args[key] = x

    if args['--output'] == 'root/data':
        # repository root dir
        args['--output'] = '%s/data' % args['root']
    
    return args


def main():
    # init args
    args = get_args(docopt(__doc__, version=__version__))
    
    # extract
    main_process = Main(args)
    main_process.extract()


if __name__ == '__main__':
    main()
