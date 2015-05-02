# DistantTermExtractor
Distant Supervision による用語抽出を行います．

## 使い方
`python scripts/main.py -h`  
```
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
```


例  
`python scripts/main.py -c 自動車工学 -l log.txt`  


`-o`オプションで指定したディレクトリに様々なファイルが出力されます．  
（指定しない場合は`./data`ディレクトリが作成されます．）  
最終的に獲得した単語は`./data/output/fp_words.txt`に出力されます．  

## 必要なツール
* docopt
* CRF++ 
* mecab
* unidic-mecab

docoptはpipで，CRF++は[サイト][CRF++]から，unidic-mecabも[サイト][unidic]から  
unidic-mecabはbinバージョンをダウンロードしてください．  
そして，展開した中身から`dicrc`**以外**をリポジトリのmy_unidicにコピーしてください．  

[CRF++]: http://taku910.github.io/crfpp/
[unidic]: http://sourceforge.jp/projects/unidic/

