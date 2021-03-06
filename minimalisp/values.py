from __future__ import print_function

def crepr(s):
    assert type(s) is str, "crepr is for strings, i.e. str() instances."
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
    if type(s) is str:
        return crepr(s)
    return repr(s)


class LispType(object):
    pass


class Symbol(LispType):
    """only stores its text representation as a python string in upper case
    - can therefore be used as a dict key."""
    def __init__(self, s, quoted=False):
        self.s = s.upper()
        self.quoted = quoted

    def __eq__(self, other):
        if type(other) is not Symbol:
            return False
        return self.s == other.s

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        if self.quoted:
            return "'" + self.s
        return self.s

    def __hash__(self):
        return hash(self.s)


class LispValue(LispType):
    pass


class NIL(LispValue):
    def __eq__(self, other):
        return isinstance(other, NIL)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'NIL'


class Value(LispValue):
    """stored simply as the relevant python type (string, int or float)."""
    def __init__(self, v, actual=False):
        if actual:
            self.v = v
        else:
            self.v = eval(v)

    def __eq__(self, other):
        if not isinstance(other, Value):
            return False
        return self.v == other.v

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        if isinstance(self.v, (str, unicode)):
            return self.v
        else:
            return repr(self.v)


class Pair(LispType):
    def __init__(self, left=None, right=None, quoted=False):
        self.left = left
        self.right = right
        self.quoted = quoted

    def __eq__(self, other):
        if not isinstance(other, Pair):
            return False

        # This is recursive for large pair structures, and should test equality of all
        # leaf values.

        # We change the order to avoid making depth-first the enemy of speed (one side may be a
        # single different value, the other may be a large, equal linked list.)
        left_is_pair = isinstance(self.left, Pair) and isinstance(other.left, Pair)
        right_is_pair = isinstance(self.right, Pair) and isinstance(other.right, Pair)

        if left_is_pair and not right_is_pair:
            return (self.right == other.right and self.left == other.left)

        return (self.left == other.left and self.right == other.right)

    def __ne__(self, other):
        return not self == other


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
