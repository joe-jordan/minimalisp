
class NIL(object):
    def __repr__(self):
        return 'NIL'

def crepr(s):
    assert isinstance(s, str), "crepr is for strings, i.e. str() instances."
    prepr = repr(s)
    if prepr[:3] == '"""':
        # anything goes, need to manually escape everything.
        raise NotImplementedError("not implemented for this repr type.")
    elif prepr[0] == '"':
        return prepr
    else:
        assert prepr[0] == "'", "unknown repr output from python."
        return '"' + prepr[1:-1].replace("\\'", "'").replace('"', '\\"') + '"'


def lrepr(s):
    if isinstance(s, str):
        return crepr(s)
    return repr(s)


class MinimalispType(object):
    pass

class Symbol(MinimalispType):
    """only stores its text representation as a python string in upper case
    - can therefore be used as a dict key."""
    def __init__(self, s):
        self.s = s.upper()

    def __eq__(self, other):
        if other is not Symbol:
            return False
        if self.s == other.s:
            return True

    def __repr__(self):
        return self.s

    def __hash__(self):
        return hash(self.s)


class Value(MinimalispType):
    """stored simply as the relevant python type (string, int or float)."""
    def __init__(self, v):
        self.v = eval(v)
    
    def __repr__(self):
        if isinstance(self.v, str):
            return crepr(self.v)
        else:
            return repr(self.v)

class Pair(MinimalispType):
    def __init__(self, left=None, right=None, quoted=False):
        self.left = left
        self.right = right
        self.quoted = quoted

    @classmethod
    def pair_list_from_sexpr(cls, s, outermost_quoted = False):
        right = NIL()
        for v in reversed(s):
            right = Pair(v, right)
        if outermost_quoted:
            right.quoted = True
        return right
    
    def __repr__(self):
        q = ""
        if self.quoted:
            q = "'"
        return "%s(%s . %s)" % (q, self.left, self.right)
