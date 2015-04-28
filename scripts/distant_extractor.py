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


class DistantExtractor():

    u"""
    seedとunlabeledデータが渡された時に勝手にラベルをつけて学習するようにする
    wikipedia周りは別にやらせる
    """

    def __init__(self, root_cat, depth, logger):
        self._logger = logger
        self._root_cat = root_cat
        self._limit_depth = depth
        self._seeds = list()
        self._categories = [self._root_cat]
        self._wiki_extractor = WikipediaExtractor(
            mylogger.get_logger(
                WikipediaExtractor.__name__,
                mylogger.get_filename(logger),
                mylogger.DEBUG
            )
        )

    def extract_seed(self):
        self._logger.info('\n------extract seed------')
        self._logger.info('depth 0')
        current_depth = 0

        # Wikipedia API
        for cat in self._categories:
            new_seeds, new_cats = self._wiki_extractor.get_subcategories_titles(cat)  # noqa
            self._logger.info('%d seeds from category %s' % (len(new_seeds), cat))  # noqa
            self._seeds += new_seeds

            # add subcategories to extract
            if current_depth != self._limit_depth:
                self._logger.info('%d categories from category %s' % (len(new_cats), cat))  # noqa
                self._categories += new_cats
                current_depth += 1
                self._logger.info('depth %d' % current_depth)

    def extract_unlabeled_data(self, file_writer):
        self._logger.info('\n------extract unlabeled data--------')

        # Wikipedia API
        for title in self._seeds:
            content = self._wiki_extractor.get_content(title)
            file_writer.write_string(
                content, 'unlabeled_corpora', '%s.txt' % title)

    def pre_process(self):
        # 文分割
        # mecab
        # mecab出力の調整
        # 素性追加
        # ラベリング
        pass

    def labeling(self):
        pass
    
    def add_feature(self):
        pass
    
    def cleaning(self):
        pass

    def decoding(self):
        pass

    def fp_extract(self):
        pass

    def filtering(self):
        pass

    def get_seeds(self):
        return self._seeds


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

    # init logger
    de_logger = mylogger.get_logger(
        DistantExtractor.__name__,
        args['--log'],
        mylogger.DEBUG
    )
    wr_logger = mylogger.get_logger(
        FileWriter.__name__,
        args['--log'],
        mylogger.DEBUG
    )
    wiki_logger = mylogger.get_logger(
        WikipediaExtractor.__name__,
        args['--log'],
        mylogger.DEBUG
    )

    # init
    writer = FileWriter(args.output_dir, wr_logger)
    de = DistantExtractor(args.root_cat, args.depth, de_logger)

    # extract from Wikipedia
    de.extract_seed()
    writer.write_list(de.get_seeds(), 'seeds', 'seed')
    de.extract_unlabeled_data(writer)


if __name__ == '__main__':
    main()
