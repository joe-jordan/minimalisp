#! /usr/bin/env python
# If you get an import error here, please use python >= 2.6 .
from __future__ import print_function
import fileinput, re

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


class MinimalispType(object):
    pass


class Pair(MinimalispType):
    instances = []
    
    @classmethod
    def fixall(cls):
        for i in cls.instances:
            i.fix()
    
    def __init__(self, quoted=False):
        self.quoted = quoted
        self.left = None
        self.right = None
        Pair.instances.append(self)
    
    def set_next(self, value):
        assert value != self, "cannot add a pair to itself."
        if self.left == None:
            self.left = value
        assert self.right == None, "tried to set next on a completed pair"
        self.right = value
    
    def set_left(self, new_left):
        assert self.left == None
        self.left = new_left
    
    def set_right(self, new_right):
        assert self.right == None
        self.right = new_right
    
    def fix(self):
        if self.left == None:
            self.left = NIL()
        if self.right == None:
            self.right = NIL()
    
    def is_empty(self):
        return self.right == None and self.left == None
    
    def __contains__(self, item):
        if self.left is item or self.right is item:
            return True
        return False
    
    def __repr__(self):
        quote = ''
        if self.quoted:
            quote = "'"
        return quote + '(' + repr(self.left) + ' . ' + repr(self.right) + ')'


class Symbol(MinimalispType):
    """only stores its text representation as a python string in upper case
    - can therefore be used as a dict key."""
    def __init__(self, s):
        self.s = s.upper()
    
    def __repr__(self):
        return self.s


class Value(MinimalispType):
    """stored simply as the relevant python type (string, int or float)."""
    def __init__(self, v):
        self.v = eval(v)
    
    def __repr__(self):
        if isinstance(self.v, str):
            return crepr(self.v)
        else:
            return repr(self.v)


BEGIN_PAIR = "'("
BEGIN_QUOTED_PAIR = "'"
END_PAIR = ')'
PAIR_SEPARATOR = '.'

WHITESPACE = " \t\r\n"

NUMERIC = "0123456789"
BEGIN_HEXANUMERIC = "#"
HEXANUMERIC = NUMERIC + "ABCDEF"

STRINGY = '"'

def parse():
    lines = [line.strip() for line in fileinput.input()]
    
    # in theory, this should be done with a RE. however, expressing "an even
    # number of non-escaped double quotes, followed by a semicolon" as a regex
    # is more of a headache than it is worth.
    
    commentless_lines = []
    
    for l in lines:
        splits = [s for s in reversed(l.split(';'))]
        if len(splits) == 1:
            commentless_lines.append(l)
            continue
        
        previous_string = splits.pop()
        
        while len(re.findall(r'(?<!\\)"', previous_string)) % 2 != 0:
            previous_string += ';' + splits.pop()
        
        commentless_lines.append(previous_string)
    
    text = ''.join(commentless_lines)
    
    buffer_index = 0
    buffer_length = len(text)
    
    assert text[buffer_index] in BEGIN_PAIR, "not a minimalisp program"
    
    pairs = []
    
    context = {
        'parent' : None,
        'dots' : 0,
        'sexpr_level' : 0
    }
    
    last_char_was_dot = False
    
    while buffer_index < buffer_length:
        
        if text[buffer_index] in BEGIN_PAIR:
            # we are entering a new context:
            if text[buffer_index] in BEGIN_QUOTED_PAIR:
                pair = Pair(quoted=True)
                buffer_index += 1
                assert text[buffer_index] in BEGIN_PAIR, "quote not followed by an open parenthesis."
            else:
                pair = Pair()
            
            # if we're already in an S-expression context, we need to add this 
            # pair to the left of a new non-quoted pair in the S-expression.
            if context['sexpr_level']:
                spair = Pair()
                spair.set_left(pair)
                context['pair'].set_right(spair)
                context = {
                    'parent' : context,
                    'pair' : spair,
                    'dots' : 0,
                    'sexpr_level' : context['sexpr_level'] + 1
                }
            
            context = {
                'parent' : context,
                'pair' : pair,
                'dots' : 0,
                'sexpr_level' : 0
            }
            buffer_index += 1
            last_char_was_dot = False
            continue
        elif text[buffer_index] in WHITESPACE:
            pass
        elif text[buffer_index] in PAIR_SEPARATOR:
            assert context['pair'].left != NIL, " ( followed by . is disallowed."
            assert last_char_was_dot == False, " . followed by . is disallowed."
            assert context['dots'] == 0, "multiple . in one set of parens disallowed."
            
            context['dots'] += 1
            last_char_was_dot = True
            
        elif text[buffer_index] in END_PAIR:
            assert last_char_was_dot == False, " . followed by ) is disallowed."
            
            # raise context level.
            if context['pair'].is_empty():
                context['pair'] = NIL()
            
            # unwind any S-expr contexts.
            while context['sexpr_level']:
                context = context['parent']
            
            try:
                if context['pair'] not in context['parent']['pair']:
                    context['parent']['pair'].set_next(context['pair'])
            except KeyError:
                # if this is the root file scope, we just append to the list of statements.
                pairs.append(context['pair'])
            
            context = context['parent']
        else:
            # character is a valid symbol or literal character, indeed the first in a new literal.
            token_start = buffer_index
            char1 = text[buffer_index]
            
            DUBIOUS = "+-"
            
            # shift the decision onto the second char.
            if char1 in DUBIOUS:
                # check ahead to see what type we're dealing with.
                if text[buffer_index+1] in WHITESPACE:
                    # this is a single + or - as a symbol. do nothing.
                    pass
                elif text[buffer_index+1] in NUMERIC:
                    # if numeric, just set char1 so that the next loop runs properly.
                    char1 = text[buffer_index+1]
            
            is_num = False
            is_hex = False
            is_string = False
            is_symbol = False
            
            if char1 in NUMERIC:
                is_num = True
                buffer_index += 1
                contains_decimal = False
                contains_exponent = False
                while text[buffer_index] in '.' + NUMERIC:
                    buffer_index += 1
                    if text[buffer_index] == '.':
                        contains_decimal = True
                        buffer_index += 1
                        break
                if contains_decimal:
                    while text[buffer_index] in 'eE' + NUMERIC:
                        buffer_index += 1
                        if text[buffer_index] in 'eE':
                            contains_exponent = True
                            buffer_index += 1
                            break
                if contains_exponent:
                    while text[buffer_index] in DUBIOUS + NUMERIC:
                        buffer_index += 1
                assert text[buffer_index] in WHITESPACE + END_PAIR, "ill formed number."
            elif char1 in BEGIN_HEXANUMERIC:
                is_hex = True
                buffer_index += 1
                while text[buffer_index].upper() in HEXANUMERIC:
                    buffer_index += 1
            elif char1 in STRINGY:
                is_string = True
                buffer_index += 1
                while True:
                    if text[buffer_index] in STRINGY and not text[buffer_index-1] == '\\':
                        buffer_index += 1
                        break
                    buffer_index += 1
            else:
                is_symbol = True
                buffer_index += 1
                while text[buffer_index] not in WHITESPACE + PAIR_SEPARATOR + END_PAIR:
                    buffer_index += 1
            
            token = text[token_start:buffer_index]
            
            if is_num or is_string:
                v = Value(token)
            elif is_hex:
                token = token.replace('#', '0x')
                v = Value(token)
            elif is_symbol:
                if token.upper() == "NIL":
                    v = NIL()
                else:
                    v = Symbol(token)
            else:
                raise Exception()
            
            # if the current pair is empty, we assign to the left of it:
            if context['pair'].is_empty():
                context['pair'].set_left(v)
            else:
                if last_char_was_dot:
                    # in this instance only, we assign a non-pair to a pair.right:
                    context['pair'].set_right(v)
                else:
                    # in all other cases, we assign a new pair, without changing context.
                    new_pair = Pair()
                    new_pair.set_left(v)
                    context['pair'].set_right(new_pair)
                    
                    context = {
                        'parent' : context,
                        'pair' : new_pair,
                        'dots' : 0,
                        'sexpr_level' : context['sexpr_level'] + 1
                    }
                
            
            # continue without incrementing further, in case the next char requires processing.
            last_char_was_dot = False
            continue
        
        # several of the elifs just drop down into here.
        buffer_index += 1
    
    assert context['parent'] == None, "parentheses not matched."
    
    Pair.fixall()
    
    return pairs


def run(program):
    pass


if __name__ == "__main__":
    import pycatch
    pycatch.enable(ipython=True)
    
    program = parse()
    
    for p in program:
        print(repr(p))
    
    run(program)
    