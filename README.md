# ppchyprep

Code to prepare the Penn Parsed Corpus of Historical Yiddish (PPCHY) for NLP work

## Purpose

The part-of-speech tagger discussed [here](https://arxiv.org/abs/2204.01175) uses the PPCHY for training and evaluation material.   This code carries out various processing steps to prepare the PPCHY for that purpose.  This includes converting the romanized form to Yiddish script and creating the splits for the cross-validation training/eval experiments.  For more details please see the code documentation.

## Installation

There are two packages that need to be installed that are not yet on PyPi, 
[yiddishycode](https://github.com/skulick/yiddishycode) and 
[ppctree](https://github.com/skulick/yiddishycode).
These can be installed with
```
git clone https://github.com/skulick/yiddishycode.git
cd yiddishycode
pip install .
cd ..
git clone https://github.com/skulick/ppctree.git
cd ppcprep
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
git checkout 75bda8082a8963b5e588c1ae4c73f1af376d3626
cd ../..
pip install -r requirements.txt
```

The above also installs the PPCHY as of 4/28/23.

## Usage
The directory structure resulting from the above contains:

```
ppchyprep/run.sh
ppchyprep/data/penn-parsed-corpus-of-historical-yiddish
ppchyprep/src
```

To carry out the processing, run `./run.sh` from the `ppchyprep` directory. This is hard-coded to write the output to a `ppchyprep/out` directory. Of course this can be changed in the run.sh script as desired.

The output directories and files in `ppchyprep/out/penn2/split` are used for training the part-of-speech tagger. (This code will be included at https://github.com/skulick/yiddishtag, although is not there yet.) For further information on the output, please see the code documentation.


## Other Notes
The code uses the yiddish library at  https://github.com/ibleaman/yiddish

## Citation 
If you'd like to cite this library in a publication, you can include a link to the source: https://github.com/skulick/ppchyprep





