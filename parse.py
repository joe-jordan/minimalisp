import re

class sexpr(list):
    def __init__(self, *args, **kwargs):
        self.quoted = False
        super(sexpr, self).__init__(*args, **kwargs)

    def __repr__(self):
        outer = super(sexpr, self).__repr__()
        if self.quoted:
            return "'" + outer
        return outer

def remove_comments(inp):
    commentless_lines = []
    
    # kill comment characters ; onwards, when not inside a string.
    for l in inp.split("\n"):
        splits = l.split(';')
        if len(splits) == 1:
            commentless_lines.append(l)
            continue
        
        previous_string = splits.pop(0)
        
        while len(re.findall(r'(?<!\\)"', previous_string)) % 2 != 0:
            previous_string += ';' + splits.pop()
        
        commentless_lines.append(previous_string)
    return "\n".join(commentless_lines)


def clever_split(inp):
    commentless_inp = remove_comments(inp)
    
    # rather than splitting on all whitespace, we want to split only on 
    # whitespace not inside a string.
    # strings cannot contain newlines, so start by splitting on those:
    lines = commentless_inp.split("\n")
    tokens = []
    for i, l in enumerate(lines):
        splits = [s for s in l.split('"')]

        # if there were no "s in this line, split the whole thing by whitespace:
        if len(splits) == 1:
            tokens.extend(l.split())
            continue
        
        # first " can't be escaped.
        tokens.extend(splits.pop(0).split())

        while splits:
            this_string = splits.pop(0)
            # while the quotes are escaped:
            while this_string[-1] == "\\":
                assert len(splits) > 0, "string on line %d is not terminated correctly." % i
                this_string = this_string[:-1] + '"' + splits.pop(0)
            # we've got to the end of this string, add it as its own token:
            tokens.append('"' + this_string + '"')

            # the next tokens are not strings, so just extend them (if any):
            if splits:
                tokens.extend(splits.pop(0).split())

    return tokens

    

def parse(inp):
    toks = clever_split(inp)
    parents = {}
    output_list = sexpr()
    current_list = output_list
    while True:
        try:
            tok = toks.pop(0)
        except IndexError:
            break
        while tok and tok[0] in "'(" and (tok[0] == '(' or tok[:2] == "'("):
            current_list.append(sexpr())
            parents[id(current_list[-1])] = current_list
            current_list = current_list[-1]
            if tok[0] == '(':
                tok = tok[1:]
            else:
                tok = tok[2:]
                current_list.quoted = True
                
        end_here = 0
        while tok and tok[-1] == ')':
            end_here += 1
            tok = tok[:-1]
        if tok:
            current_list.append(tok)
        while end_here:
            end_here -= 1
            current_list = parents[id(current_list)]
    assert id(current_list) == id(output_list), "s expressions not closed"
    return output_list


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


PAIR_SEPARATOR = '.'

class PAIR_LITERAL(object):
    pass

NUMERIC = "0123456789"
BEGIN_HEXANUMERIC = "#"
HEXANUMERIC = NUMERIC + "ABCDEF"
STRINGY = '"'

DUBIOUS = "+-"
ALLOWED_IN_NUMERIC = NUMERIC + DUBIOUS + "eE."

def parse_token(t):
    char1 = t[0]
    # shift the decision onto the second char.
    if char1 in DUBIOUS:
        # check ahead to see what type we're dealing with.
        if len(t) == 1:
            # this is a single + or - as a symbol. do nothing.
            pass
        elif t[1] in NUMERIC:
            # if numeric, just set char1 so that the next section categorises properly.
            char1 = t[1]
    
    if char1 in NUMERIC:
        assert all([c in ALLOWED_IN_NUMERIC for c in t]), "token %s contains invalid characters to be a numeric literal." % t
        v = Value(t)
    elif char1 in STRINGY:

        v = Value(t)
    elif char1 in BEGIN_HEXANUMERIC:
        assert all([c in HEXANUMERIC for c in t[1:]]), "token %s contains invalid characters for a hexadecimal literal." % t
        t = t.replace('#', '0x')
        v = Value(t)
    elif char1 in PAIR_SEPARATOR:
        assert len(t) == 1, "token %s is invalid: cannot use . at the start of a symbol or literal." % t
        v = PAIR_LITERAL
    else:
        if t.upper() == "NIL":
            v = NIL()
        else:
            v = Symbol(t)
    return v


def parse_program(p):



