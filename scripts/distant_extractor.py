# coding:utf-8

import re
import subprocess
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
        #TODO 後々は複数クラスのシードを持てるようにする
        # name をkey, seeds(list)をvalueなdictにする
        # ラベリングのところはそうなってる
        self._seed_name = 'Car'
        self._seeds = list()
        self._categories = [self._root_cat]

        # init name
        self._seed_dir = 'seeds'
        self._unlabeled_dir = 'unlabeled_corpora'
        self._cleaned_dir = 'cleaned_corpora'
        self._mecab_dir = 'mecab_corpora'
        self._labeled_dir = 'labeled_corpora'
        self._train_dir = 'train_corpora'
        self._output = 'output'
        self._temp_dir = 'temp'
        self._templatefile = '%s/templates/template' % root_dir
        self._trainfile = '%s/train.txt' % output_dir
        self._decodefile = '%s/decode.txt' % output_dir
        self._modelfile = '%s/model' % output_dir
        self._all_labeledfile = '%s/all_labeled.txt' % output_dir

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
            w.close()
            r.close()

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
            w.close()
            r.close()

        self._logger.info('add feature')
        self._file_io.rewrite_files(
            self._mecab_dir,
            self._temp_dir,
            add_feat
        )

    def labeling(self):
        class_dict = dict()
        class_dict[self._seed_name] = self._seeds

        def sent2label(usent):
            # キーワードをB-label\tI-label...の形にする関数
            def word2label(uword, label):
                result = "".join(map(lambda char: u"I-" + label + u"\t", uword))
                result = u"B" + result[1:]
                return result
            
            # 辞書にマッチするキーワードがあればB-label I-labelのかたちに置き換える
            for clas in class_dict.keys():
                # 例えばエンジンイモビライザーシステムがあるときに、イモビライザーで先にマッチさせるとエンジンBIIIIIIシステムになってしまう
                # ので、文字長が長いワードから順にマッチさせるパターンを作る
                patterns = map(lambda word: re.compile(unicode(word, "utf8")), sorted(class_dict[clas], key=lambda x: -len(x)))
                # 置き換える
                usent = reduce(lambda s, pattern: pattern.sub(lambda m: word2label(m.group(), clas), s), [usent] + patterns)
            
            # B-label I-labelにマッチしない文字はすべて"O"に置き換える
            npat = u"|".join(u"B-%s|I-%s" % (unicode(c, "utf8"), unicode(c, "utf8")) for c in class_dict.keys())
            not_pattern = re.compile(npat + u"|\t")

            def replace_O(usent):
                return "".join(char if i in replace_O.l else u"O\t" for i, char in enumerate(usent)).strip()
            replace_O.l = list()
            for match in not_pattern.finditer(usent):
                replace_O.l += range(match.span()[0], match.span()[1])
            usent = replace_O(usent)
          
            return usent.split("\t")

        def add_label(buf_sent, labels):
            sufs = [mout.split()[0].decode("utf8") for mout in buf_sent]
            
            last_spl = 0
            spl_labels = list()
            for suf in sufs:
                spl_labels.append(labels[last_spl:last_spl + len(suf)])
                last_spl += len(suf)
            
            for i, spl_label in enumerate(spl_labels):
                I_flag = ""
                B_flag = False
                for clas in class_dict.keys():
                    if u"B-" + unicode(clas, "utf8") in spl_label and not B_flag:
                        buf_sent[i] += " B-" + clas
                        B_flag = True
                    if u"I-" + unicode(clas, "utf8") in spl_label:
                        I_flag = clas
                if not B_flag and I_flag:
                    buf_sent[i] += " I-" + I_flag
                elif not B_flag:
                    buf_sent[i] += " O"

            return buf_sent

        def sent_labeling(buf_sent):
            # surfaceだけつなげて1文を作る
            sent = "".join(mout.split()[0] for mout in buf_sent)
            # 1文の文字にラベルを振る
            labels = sent2label(unicode(sent, "utf-8"))
            # mecabの形式にラベルを振る
            buf_sent = add_label(buf_sent, labels)

            return buf_sent

        def label(wf, rf):
            w = open(wf, 'w')
            r = open(rf)

            buffer_sent = list()
            sent_count = 0

            for line in r:
                line = line.strip()
                if line == "":
                    sent_count += 1
                    for mecab_out_tok in sent_labeling(buffer_sent):
                        w.write('%s\n' % mecab_out_tok)
                    w.write('\n')
                    buffer_sent = list()
                else:
                    buffer_sent.append(line.strip())

        self._logger.info('labeling')
        self._file_io.rewrite_files(
            self._temp_dir,
            self._labeled_dir,
            label
        )

    def train(self):
        # create train data
        def remove_only_o(wf, rf):
            w = open(wf, 'w')
            r = open(rf)
            flag = False
            sent = str()
            for line in r:
                sent += line
                if line.strip() != "" and line.strip().split()[-1] != "O":
                    flag = True
                if line.strip() == "":
                    if flag:
                        w.write(sent)
                    flag = False
                    sent = str()

        self._logger.info('create train data')
        self._file_io.rewrite_files(
            self._labeled_dir,
            self._train_dir,
            remove_only_o
        )
        self._file_io.cat(self._train_dir, self._trainfile)

        # train
        self._logger.info('train by crf')
        
        lf = mylogger.get_filename(self._logger)
        if lf is None:
            cmd = 'crf_learn -t -p4 -f 3 -c 5.0 %s %s %s' % (self._templatefile, self._trainfile, self._modelfile)
        else:
            cmd = 'crf_learn -t -p4 -f 3 -c 5.0 %s %s %s >> %s' % (self._templatefile, self._trainfile, self._modelfile, lf)
        subprocess.call(cmd, shell=True)

    def decode(self):
        self._logger.info('create all labeled file')
        self._file_io.cat(self._labeled_dir, self._all_labeledfile)
        
        self._logger.info('decode by crf')
        cmd = 'crf_test -m %s %s> %s' % (self._modelfile, self._all_labeledfile, self._decodefile)
        subprocess.call(cmd, shell=True)

    def extract_fp(self):
        self._file_io.mkdir(self._output)
        def diff(fw, fr):
            w = open(fw, 'w')
            r = open(fr)
            phrase = str()
            gBIflag = False
            sBIflag = False
            catchFlag = False
            
            for line in r:
                if line.strip() == "":
                    phrase = str()
                    continue
                sys = line.strip().split()[-1]
                gold = line.strip().split()[-2]
                
                if gold != "O":
                    gBIflag = True
                if sys != "O":
                    sBIflag = True
                if gold == "O":
                    gBIflag = False
                if sys == "O":
                    sBIflag = False

                if gold != sys:
                    catchFlag = True

                if not gBIflag and not sBIflag:
                    if catchFlag:
                        w.write('%s\n' % phrase)
                        catchFlag = False
                    phrase = str()
                    continue
                phrase += line
            w.close()
            r.close()
        
        self._logger.info('decode diff')
        self._file_io.rewrite_file(
            self._decodefile,
            '%s/diff.txt' % self._output,
            diff
        )

        def spl_diff(wf1, wf2, rf):
            r = open(rf)
            wfp = open(wf1, 'w')
            wfn = open(wf2, 'w')
            phrase = str()
            for line in r:
                if line.strip() == "":
                    try:
                        if "fp" in map(lambda l: "fp" if l.split()[-2]=="O" else "x", phrase.strip().split("\n")):
                            wfp.write(phrase+"\n")
                        else:
                            wfn.write(phrase+"\n")
                    except IndexError:
                        self._logger("IndexError: pharase>"+phrase+"<")
                    phrase = str()
                    continue
                phrase += line
            r.close()
            wfp.close()
            wfn.close()

        self._logger.info('split diff to fp and fn')
        self._file_io.rewrite_file2(
            '%s/diff.txt' % self._output,
            '%s/fp.txt' % self._output,
            '%s/fn.txt' % self._output,
            spl_diff
        )

        def get_tp(fw, fr):
            w = open(fw, 'w')
            r = open(fr)
            phrase=str()
            Bflag = False
            for line in r:
                if line.strip()=="":
                    continue
                gol = line.strip().split()[-2]
                sys = line.strip().split()[-1]
                
                if gol[0] == "B" and sys[0] == "B" and not Bflag:
                    Bflag = True
                    phrase+=line
                elif gol[0] == "I" and sys[0] == "I" and Bflag:
                    phrase+=line
                elif gol[0] == "B" and sys[0] == "B":
                    w.write('%s\n' % phrase)
                    phrase = line
                else:
                    Bflag = False
                    if phrase:
                        w.write('%s\n' % phrase)
                        phrase=str()
            w.close()
            r.close()

        self._logger.info('get tp')
        self._file_io.rewrite_file2(
            '%s/diff.txt' % self._output,
            '%s/tp.txt' % self._output,
            spl_diff
        )

        def get_word_from_diff(fw, fr):
            w = open(fw, 'w')
            r = open(fr)
            word = list()
            l = list()
            for line in r:
                if line.strip() == "":
                    l.append(("///".join(word), cl))
                    word = list()
                    continue
                if line.strip().split()[-1][0]=="B":
                    cl = line.strip().split()[-1][2:]
                    word.append(line.strip().split()[0])
                elif line.strip().split()[-1]=="O" and line.strip().split()[-2][0]=="B":
                    word.append(line.strip().split()[0])
                    cl = line.strip().split()[-2][2:]
                else:
                    word.append(line.strip().split()[0])
            
            for item in sorted(set(l), key=lambda x:x[1]):
                w.write('%s %s %s' % (item[0].replace("///",""), item[1], "\t"+item[0]))
            w.close()
            r.close()

        self._logger.info('get fp words')
        self._file_io.rewrite_file2(
            '%s/fp.txt' % self._output,
            '%s/fp_words.txt' % self._output,
            get_word_from_diff
        )

        self._logger.info('get fn words')
        self._file_io.rewrite_file2(
            '%s/fn.txt' % self._output,
            '%s/fn_words.txt' % self._output,
            get_word_from_diff
        )

        self._logger.info('get tp words')
        self._file_io.rewrite_file2(
            '%s/tp.txt' % self._output,
            '%s/tp_words.txt' % self._output,
            get_word_from_diff
        )

    def filtering(self):
        pass

    def get_seeds(self):
        return self._seeds
