# ppchyprep

Code to prepare the Penn Parsed Corpus of Historical Yiddish (PPCHY) for NLP work

## Purpose

The part-of-speech tagger discussed [here](https://arxiv.org/abs/2204.01175), and a syntactic parser to be released use the PPCHY for training and evaluation material.  This code carries out various processing steps to prepare the PPCHY for that purpose.

## Installation

There are two packages that need to be installed that are not yet on PyPi, 
[yiddishycode](https://github.com/skulick/yiddishycode) and 
[ppctree](https://github.com/skulick/ppctree).
These can be installed with
```
git clone https://github.com/skulick/yiddishycode.git
cd yiddishycode
pip install .
cd ..
git clone https://github.com/skulick/ppctree.git
cd ppctree
pip install .
cd ..
```

To install the rest:
```
git clone https://github.com/skulick/ppchyprep.git
cd ppchyprep
mkdir data
cd data
git clone https://github.com/beatrice57/penn-parsed-corpus-of-historical-yiddish.git
cd penn-parsed-corpus-of-historical-yiddish
git checkout 3cedddb2fa11b6873e92dbd043e29df39c8612e6
cd ../..
pip install -r requirements.txt
```

## Usage
The directory structure resulting from the above contains:

```
ppchyprep/run.sh
ppchyprep/data/penn-parsed-corpus-of-historical-yiddish
ppchyprep/src
```

To carry out the processing, run `./run.sh` from the `ppchyprep` directory, setting `NEW_CORPUS_DIR` to the desired location.

The resulting output is in the `data-mod` directory of [this fork of PPCHY](https://github.com/skulick/penn-parsed-corpus-of-historical-yiddish). 
For further information on the output, please see the code documentation.


## Other Notes
The code uses the yiddish library at  https://github.com/ibleaman/yiddish

## Citation 
If you'd like to cite this library in a publication, you can include a link to the source: https://github.com/skulick/ppchyprep





