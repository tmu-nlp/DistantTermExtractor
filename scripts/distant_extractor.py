# coding:utf-8


class DistantExtractor():

    u"""
    DistantSupervisionを使って用語を抽出するクラス.

    seedとunlabeledデータがある時に勝手にラベルをつけて学習する
    学習したらデコードして用語を抽出する
    wikipedia周りは別にやらせる
    """

    def __init__(self, root_cat, depth, logger, file_io, wiki_ex):
        self._logger = logger
        self._file_io = file_io
        self._wiki_extractor = wiki_ex
 
        self._root_cat = root_cat
        self._limit_depth = depth
        self._seeds = list()
        self._categories = [self._root_cat]

        # init dir name
        self._seed_dir = 'seeds'
        self._unlabeled_dir = 'unlabeled_corpora'
        self._cleaned_dir = 'cleaned_corpora'

    def extract_seed(self):
        self._logger.info('\n------extract seed------')
        self._logger.info('depth 0')
        current_depth = 0

        # Wikipedia API
        for cat in self._categories:
            new_seeds, new_cats = self._wiki_extractor.get_subcategories_titles(cat)  # noqa
            self._logger.info('%d seeds from category %s' % (len(new_seeds), cat))  # noqa
            if '/' in new_seeds:
                new_seeds = new_seeds.replace('/', ':')
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
            for line in wf:
                if line.strip() == '':
                    continue
                if line.startswith('関連項目'):
                    return
                spl = line.strip().replace('。', '。\n').split('\n')
                for l in spl:
                    wf.write('%s\n' % l)
            return

        self._file_io.rewrite_files(
            self._unlabeled_dir,
            self._cleaned_dir,
            clean
        )

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
    

    def decoding(self):
        pass

    def fp_extract(self):
        pass

    def filtering(self):
        pass

    def get_seeds(self):
        return self._seeds
