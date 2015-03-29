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
                this_string = this_string[:-1] + '\\"' + splits.pop(0)
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


PAIR_SEPARATOR = '.'

class PAIR_LITERALS(object):
    def __repr__(self):
        return '.'

PAIR_LITERAL = PAIR_LITERALS()


NUMERIC = "0123456789"
BEGIN_HEXANUMERIC = "#"
HEXANUMERIC = NUMERIC + "ABCDEF"
STRINGY = '"'

DUBIOUS = "+-"
ALLOWED_IN_NUMERIC = NUMERIC + DUBIOUS + "eE."

from values import Value, Symbol, NIL, Pair

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
    elif char1 in PAIR_SEPARATOR and len(t) == 1:
        v = PAIR_LITERAL
    else:
        if t.upper() == "NIL":
            v = NIL()
        elif t[0] in "'":
            v = Symbol(t[1:], True)
        else:
            v = Symbol(t)
    return v

def parse_token_prompt(t):
    v = parse_token(t)
    if v == PAIR_LITERAL:
        return Value('"."')
    elif isinstance(v, Symbol):
        return Value('"%s"' % t)
    return v


def parse_tokens(s):
    for i, t in enumerate(s):
        if type(t) == sexpr:
            parse_tokens(t)
            continue
        s[i] = parse_token(t)
        if s[i] == PAIR_LITERAL:
            assert i == 1 and len(s) == 3, "incorrect context for a pair literal, %s." % repr(s)


def do_pair_literals(s):
    for i, t in enumerate(s):
        if type(t) == sexpr:
            do_pair_literals(t)

            if len(t) == 3 and t[1] == PAIR_LITERAL:
                s[i] = Pair(t[0], t[2], t.quoted)


def sexprs_to_pairs(s):
    for i, t in enumerate(s):
        if type(t) == sexpr:
            s[i] = sexprs_to_pairs(t)
        elif type(t) == Pair:
            # was specified as a pair literal in the source, may contain s-expressions inside.
            if type(t.left) == sexpr:
                t.left = sexprs_to_pairs(t.left)
            if type(t.right) == sexpr:
                t.right = sexprs_to_pairs(t.right)
    assert all([type(t) is not sexpr for t in s]), "programming error in parser."
    return Pair.pair_list_from_sexpr(s, s.quoted)


def parse_program(inp):
   prog = parse(inp)

   # now recursively walk over all s-expressions, building tokens into Values, Symbols, and Pair Separator placeholders.
   parse_tokens(prog)

   # identify any pair literals and instantiate those first:
   do_pair_literals(prog)

   # finally, build actual Pairs for all the proper S-expressions:
   prog = sexprs_to_pairs(prog)

   return prog


