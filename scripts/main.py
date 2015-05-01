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
        取得したシードや記事本文，抽出した用語を出力するディレクトリ [default: ../data]
     -l <log_file>, --log <log_file> [dafault:]
        ログ出力先ファイル
"""

from docopt import docopt
from wikipedia_extractor import WikipediaExtractor
import mylogger
from file_writer import FileWriter

__author__ = "ryosukee"
__version__ = "0.0.0"
__date__ = "2015/03/23"


class Main():

    u"""
    seedとunlabeledデータが渡された時に勝手にラベルをつけて学習するようにする
    wikipedia周りは別にやらせる
    """

    def __init__(self):
        pass



def get_args(dopt):
    args = dict()
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

    return args


def main():
    # init args
    args = get_args(docopt(__doc__, version=__version__))
    
    # get seed
    # get unlabeled data

    # pre_prosess
        # morpheme analysis
        # fix form
        # add feature
        # labeling
    # learn crfpp
    # decode
    # extract fp
    # filtering
    # output


if __name__ == '__main__':
    main()
