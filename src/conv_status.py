from enum import Enum, auto

class ConvStatus(Enum):
    """Possible categories for conversion status of a tree.

    Each psd tree is assigned one of these categories when processed
    by convert_orig2mod.
    """
    OK = auto()
    NO_TREE_ID = auto()
    ROOT_CODE = auto()
    ROOT_META = auto()
    ROOT_REF = auto()
    HAS_BREAK = auto()
    TREE_EMPTY = auto()
    BAD_LEAF = auto()
