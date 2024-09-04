import re
from ppctree.tree.ppc_node import PPCNode

RE1 = re.compile(r'(?P<tag>.+?)(?P<extra>(\-(1|2|DBL|RSP|LFD))+)$')

class YidLeaf(PPCNode):
    """Terminal tree node for the PPCHY treebank

    Words can have a ^ with a gloss, and the POS can indices or function tags.
    A @ at the beginning or ending of the word indicates it needs to be merged.
    """
    def __init__(self, pos, word):
        super().__init__()
        self.pos = pos
        # some pos have tags or indices, -DBL, -RSP, -LDF, or -1/-2.
        # In such cases  the info is stored in pos_extra
        # can't just do split on - because some dashed stuff is part of the tag,
        # like RP-N
        mtch = RE1.search(pos)
        if mtch is None:
            self.pos = pos
            self.pos_extra = None
        else:
            group_dict = mtch.groupdict()
            self.pos = group_dict['tag']
            self.pos_extra = group_dict['extra']

        parts = word.split('^', maxsplit=1)
        if len(parts) == 1:
            text = word
            self.gloss = None
        else:
            text = parts[0]
            self.gloss = parts[1]

        self.split_before = text[0] == '@'
        self.split_after = text[-1] == '@'

        # remove @
        if self.split_before:
            text = text[1:]
        if self.split_after:
            text = text[:-1]

        self.text = text
        # children leaves if this is a combined word
        self.children = []
        # get filled in later
        # romanization of self.text
        # -LRB- -> (
        # -RRB- -> )
        # %EXCL% -> !

        self.rom = None
        self.yid = None
        self.ycode = None

    @staticmethod
    def is_nonempty_leaf():
        return True

    def mystr(self,):
        """Return a one-line string version of the node."""
        if self.pos_extra is None:
            pos = self.pos
        else:
            pos = f'{self.pos}{self.pos_extra}'
        text = self.text
        if self.split_before:
            text = '@' + text
        if self.split_after:
            text = text + '@'
        if self.gloss is not None:
            text = f'{text}^{self.gloss}'

        ret = f'({pos} {text})'
        return ret
