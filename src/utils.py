import itertools

from sent_word import Sent, Word

def read_pos_file(fname):
    """read twofiles.txt file

    Each sentence has a header with
    SENT\t<sent_num>\t<tree_id>

    where <sent_num> is a sequential numbering from 0
    A row for a token has 7 columns:
    0: token_num
    1: yivo romanization of token, taken from PPCHY
    2: pos of token, taken from PPCHY
    3: Yiddish script version of column 1 (yid1)
    4: Yiddish script version of column 2 (yid2)
    5: Yiddish script version of column 3 (yid3)
    6: ycode-representation of column 3
    7: ycode-representation of column 4
    8: ycode-representation of column 5

    Each sentence unit is also assigned a source_id of 0 or 1, for whether
    the tree_id is from the 1910 or 1947 file.

    Returns
    =======
    sents: list of Sent
    """
    def _is_divider(line):
        return line.strip() == ""

    sents = []
    with open(fname, 'r', encoding='utf-8') as fin:
        for is_divider, lines in itertools.groupby(fin, _is_divider):
            if not is_divider:
                lines = [line.rstrip('\n') for line in lines]
                assert lines[0].startswith('SENT'), 'something weird reading in pos'

                sent_header_parts = lines[0].split('\t')
                (_, sent_num, tree_id) = sent_header_parts
                source_id = (0 if tree_id.startswith('1910') else 1)

                token_parts_lines = [line.split('\t') for line in lines[1:]]
                assert len(token_parts_lines[0]) == 9, \
                    f'unexpected line length {token_parts_lines[0]}'
                # col 0 is token_num
                words = [Word(*cols[1:])
                         for cols in token_parts_lines]
                sent = Sent(int(sent_num), tree_id, source_id, words)
                sents.append(sent)
    return sents
