from ppctree.tree.ppc_node import PPCNode

class YidLeaf(PPCNode):
    """Terminal tree node for the PPCHY treebank

    Only difference is that the words can have a ^ with a gloss
    """
    def __init__(self, pos, word):
        super().__init__()
        self.pos = pos
        parts = word.split('^', maxsplit=1)
        if len(parts) == 1:
            self.text = word
            self.gloss = None
        else:
            self.text = parts[0]
            self.gloss = parts[1]

        # get filled in later
        self.yivo = None
        self.yid1 = None
        self.ycode1 = None
        self.yid2 = None
        self.ycode2 = None


    @staticmethod
    def is_nonempty_leaf():
        return True

    def mystr(self,):
        """Return a one-line string version of the node."""
        if self.gloss is None:
            ret = f'({self.pos} {self.text})'
        else:
            ret = f'({self.pos} {self.text}^{self.gloss})'
        return ret
