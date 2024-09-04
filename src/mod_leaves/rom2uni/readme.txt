Code to convert romanized version in treebank to yiddish script.

Our concern here is to convert the Yiddish treebank representation back
to the yiddish script version.

This mostly relies on the detransliteration function in the yiddish.py package
but with some accessory files.

(1) rompos2uni_lookup.txt:
There are various cases where the desired form is not returned by
yiddish.detransliterate.  Sometimes this is because the romanization is
ambiguous, and detransliterate returns one form.  So here various
cases are listed as lookup-exceptions to calling detransliterate, and the
POS tag is used to determine the desired detransliteration.  Also has some
assorted special cases.

(2) rompos_removehyphen.txt:
a few cases for which detransliterate returns the desired form only
if the hyphen is removed.

(3) rompos_keephyphen.txt:
The usual processing is to split words with a hyphen and convert each
part separately, but these are cases in which it has to be kept as a
unit with the hyphen to get the correct detransliteration.

(4) rompos_lkfalse.txt
detransliteration has a boolean loshn_koydesh option. The default in the code
is to use loshn_koydesh=True, unless it's one of these cases.
