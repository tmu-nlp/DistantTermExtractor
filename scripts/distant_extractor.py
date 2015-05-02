# coding:utf-8

import re
import mylogger
from file_io import FileIO
from wikipedia_extractor import WikipediaExtractor
from morpheme_tagger import MorphemeTagger


class DistantExtractor():

    u"""
    DistantSupervisionを使って用語を抽出するクラス.

    seedとunlabeledデータがある時に勝手にラベルをつけて学習する
    学習したらデコードして用語を抽出する
    wikipedia周りは別にやらせる
    """

    def __init__(self, root_cat, depth, log_file, output_dir, root_dir):
        # init logger
        self._logger = mylogger.get_logger(
            DistantExtractor.__name__,
            log_file,
            mylogger.DEBUG
        )
        io_logger = mylogger.get_logger(
            FileIO.__name__,
            log_file,
            mylogger.DEBUG
        )
        wiki_logger = mylogger.get_logger(
            WikipediaExtractor.__name__,
            log_file,
            mylogger.DEBUG
        )
        morph_logger = mylogger.get_logger(
            MorphemeTagger.__name__,
            log_file,
            mylogger.DEBUG
        )
        
        # init instance
        self._file_io = FileIO(output_dir, io_logger)
        self._wiki_extractor = WikipediaExtractor(wiki_logger, self._file_io)
        self._morpheme_tagger = MorphemeTagger(morph_logger, root_dir)
        
        # init args
        self._root_cat = root_cat
        self._limit_depth = depth
        self._seeds = list()
        self._categories = [self._root_cat]

        # init dir name
        self._seed_dir = 'seeds'
        self._unlabeled_dir = 'unlabeled_corpora'
        self._cleaned_dir = 'cleaned_corpora'
        self._mecab_dir = 'mecab_corpora'
        self._temp_dir = 'temp'

    def extract_seed(self):
        self._logger.info('\n------extract seed------')
        self._logger.info('depth 0')
        current_depth = 0

        # Wikipedia API
        for cat in self._categories:
            new_seeds, new_cats = self._wiki_extractor.get_subcategories_titles(cat)  # noqa
            self._logger.info('%d seeds from category %s' % (len(new_seeds), cat))  # noqa
            new_seeds = map(lambda s: s.replace('/', ':'), new_seeds)
            self._seeds += new_seeds

            # add subcategories to extract
            if current_depth != self._limit_depth:
                self._logger.info('%d categories from category %s' % (len(new_cats), cat))  # noqa
                self._categories += new_cats
                current_depth += 1
                self._logger.info('depth %d' % current_depth)
        # output
        self._file_io.write_list(self._seeds, self._seed_dir, 'seed')

    def extract_unlabeled_data(self):
        self._logger.info('\n------extract unlabeled data--------')

        # Wikipedia API
        for title in self._seeds:
            content = self._wiki_extractor.get_content(title)
            self._file_io.write_string(
                content, self._unlabeled_dir, '%s.txt' % title)

    def cleaning(self):
        u"""
        ラベルなしコーパスのクリーニングをする.

        1. 空行を削除
        2. 読点毎に行分割
        3. 関連項目が以降は無視
        """
        def clean(wf, rf):
            w = open(wf, 'w')
            r = open(rf)
            for line in r:
                if line.strip() == '':
                    continue
                if line.startswith('関連項目'):
                    break
                spl = line.strip().replace('。', '。\n').split('\n')
                for l in spl:
                    if l == '':
                        continue
                    w.write('%s\n' % l)
            w.close()
            r.close()
            return

        self._logger.info('cleaning')
        self._file_io.rewrite_files(
            self._unlabeled_dir,
            self._cleaned_dir,
            clean
        )

    def morpheme_tagging(self):
        self._logger.info('morpheme tagging')
        self._file_io.rewrite_files(
            self._cleaned_dir,
            self._temp_dir,
            self._morpheme_tagger.parse
        )

        self._logger.info('normalize morpheme taged format')

        def norm(wf, rf):
            w = open(wf, 'w')
            r = open(rf)
            for line in r:
                if line.strip() == '':
                    w.write('\n')
                    continue
                spl = line.strip().split()
                spll = spl[1].split('-')
                spll += ['*'] * 3
                w.write('%s %s %s %s\n' % (spl[0], spll[0], spll[1], spll[2]))
        self._file_io.rewrite_files(
            self._temp_dir,
            self._mecab_dir,
            norm
        )
        self._file_io.remove_dir(self._temp_dir)

    def add_feature(self):
        def is_katakana(ustr):
            re_kana = re.compile(u'([ァ-ヶー]|[ｱ-ﾞ])+$')
            if re_kana.search(ustr) is not None:
                return True

        def is_alpha(ustr):
            re_alpha = re.compile(u'([a-z]|[A-Z]|[Ａ-Ｚ]|[ａ-ｚ])+$')
            if re_alpha.search(ustr) is not None:
                return True

        def add_feat(wf, rf):
            w = open(wf, 'w')
            r = open(rf)
            for line in r:
                if line.strip() == '':
                    w.write('\n')
                    continue
                lsplit = line.strip().split(' ')
                word = unicode(lsplit[0], 'utf-8')

                # add tail 4 characters
                lsplit.insert(1, word[-4:].encode('utf8'))

                # add tail 3 characters
                lsplit.insert(1, word[-3:].encode('utf8'))

                # add tail 2 characters
                lsplit.insert(1, word[-2:].encode('utf8'))

                # add head 4 characters
                lsplit.insert(1, word[:4].encode('utf8'))

                # add head 3 characters
                lsplit.insert(1, word[:3].encode('utf8'))

                # add head 2 characters
                lsplit.insert(1, word[:2].encode('utf8'))

                # add katakana or alphabet
                if is_katakana(word):
                    lsplit.insert(1, 'katakana')
                elif is_alpha(word):
                    lsplit.insert(1, 'alpha')
                else:
                    lsplit.insert(1, 'Other')

                w.write('%s\n' % ' '.join(lsplit))

        self._logger.info('add feature')
        self._file_io.rewrite_files(
            self._mecab_dir,
            self._temp_dir,
            add_feat
        )

    def labeling(self):
        pass

    def decoding(self):
        pass

    def fp_extract(self):
        pass

    def filtering(self):
        pass

    def get_seeds(self):
        return self._seeds
