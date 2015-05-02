# DistantTermExtractor

## 使い方
`python scripts/main.py -h`  
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
unidic-mecabはbinバージョンをダウンロードして，中身のdicrc以外をリポジトリのmy_unidicにコピーしてください．  

[CRF++]: http://taku910.github.io/crfpp/
[unidic]: http://sourceforge.jp/projects/unidic/

