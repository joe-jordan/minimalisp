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


def lrepr(s):
    if isinstance(s, str):
        return crepr(s)
    return repr(s)


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
	    return
        
        assert id(value) != id(self.left), "tried to add the left of a pair to the right, parser error."
	try:
            assert self.right == None, "tried to set next on a completed pair"
        except AssertionError:
            print("error in pair construction, %s cannot be extended." % repr(self))
            raise
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


BEGIN_PAIR = "'("
BEGIN_QUOTED_PAIR = "'"
END_PAIR = ')'
PAIR_SEPARATOR = '.'

WHITESPACE = " \t\r\n"

NUMERIC = "0123456789"
BEGIN_HEXANUMERIC = "#"
HEXANUMERIC = NUMERIC + "ABCDEF"

STRINGY = '"'

def parse(source):
    lines = [line.strip() for line in source.split('\n')]

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

    # count a \n as a space for the purposes of syntax
    text = ' '.join(commentless_lines).strip()
    
    buffer_index = 0
    buffer_length = len(text)
    
    assert text[buffer_index] in BEGIN_PAIR, "not a minimalisp program (error near %s)" % \
                                             text[buffer_index:buffer_index+10]
    
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
                assert text[buffer_index] in BEGIN_PAIR, "quote not followed by an open parenthesis near %s." % \
                                                         text[buffer_index:buffer_index+10]
            else:
                pair = Pair()
            
            # if we're already in an S-expression context, we need to add this 
            # pair to the left of a new non-quoted pair in the S-expression.
            if context['parent'] is not None:
                print("foo")
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
            
            sexpr_was = context['sexpr_level']
            orig_parent = context
            # unwind any S-expr contexts.
            while context['sexpr_level']:
                context = context['parent']
            
            try:
                if context['pair'] not in context['parent']['pair']:
                    try:
                        context['parent']['pair'].set_next(context['pair'])
                    except AssertionError:
                        print("parser error near %s" % text[buffer_index-10:buffer_index+10])
                        raise
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

    # convert a python list of pairs to an S-expression.
    program = Pair()
    program.set_left(pairs[0])

    cursor = program

    for p in pairs[1:]:
        cursor.set_right(Pair())
        cursor = cursor.right
        cursor.set_left(p)

    Pair.fixall()
    
    return program


class Context(dict):
    """stack-like dictionary."""
    def __init__(self, *args, **kwargs):
        # default arg that can only be specified by keyword. Python 3 fixes this problem.
        parent = kwargs.pop('parent', None)
        self.parent = parent
        super(Context, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        try:
            return super(Context, self).__getitem__(key)
        except KeyError:
            if self.parent is None:
                raise

        return self.parent[key]


class LispRuntimeError(BaseException):
    pass

# evaluate - should be an object or a pair.
def peval(o, context):
    # if object is literal or quoted:
    if o is Value or (o is Pair and o.quoted):
        return o

    # if object is a bound symbol, substitute its value:
    if o is Symbol:
        return context[o]

    # if o is a function:
    if o is LispFunction:
        raise LispRuntimeError("cannot evaluate a function")

    # in other cases, o must be a pair.
    if not isinstance(o, Pair):
        raise LispRuntimeError("cannot evaluate %s", o)
    pair = o

    # in which case, if we have been asked to run a function!
    if pair.left is not Symbol:
        raise LispRuntimeError("not a symbol %s" % pair.left)

    try:
        function = context[pair.left]
    except KeyError:
        raise LispRuntimeError("unbound symbol %s" % pair.left)

    if function is not LispFunction:
        raise LispRuntimeError("symbol %s is not bound to a function, but %s" % (repr(pair.left), repr(function)))

    return function.execute(pair.right, context)


class LispFunction(MinimalispType):
    pass


class UserLispFunction(LispFunction):
    def __init__(self, argbindings, functionbody):
        self.argbindings = argbindings

        # functionbody should be copied into a new head pair, minus the quoted status.
        self.functionbody = Pair()
        self.functionbody.set_left(functionbody.left)
        self.functionbody.set_right(functionbody.right)

    def execute(self, ap, outer_context):
        # initialise a new context, with arguments bound to names specified (or NIL if none passed):
        context = Context(parent=outer_context)
        ab = self.argbindings
        while ab is not NIL:
            try:
                context[ab.left] = ap.left
            except AttributeError:
                context[ab.left] = NIL()
            ab = ab.right
            try:
                ap = ap.right
            except AttributeError:
                pass

        # eval each line of code in the function:
        fb = self.functionbody
        retval = NIL()
        while fb is not NIL:
            retval = peval(fb.left, context)
            fb = fb.right

        return retval


class BindFunction(LispFunction):
    @staticmethod
    def execute(pair, context):
        if not isinstance(pair.left, Symbol):
            raise LispRuntimeError('cannot bind value %s to non-symbol %s' % (repr(pair.right), repr(pair.left)))
        context[pair.left] = peval(pair.right, context)
        return NIL()


class WithFunction(LispFunction):
    @staticmethod
    def execute(pair, context):
        # unwind with's arguments; two quoted pairs.
        argbindings = pair.left
        if argbindings is not Pair or not argbindings.quoted:
            raise LispRuntimeError('with arg1 not satisfied, %s is not a quoted list.' % repr(argbindings))

        pair = pair.right
        functionbody = pair.left
        if functionbody is not Pair or not functionbody.quoted:
            raise LispRuntimeError('with arg2 not satisfied, %s is not a quoted list.' % repr(functionbody))

        if pair.right is not NIL:
            raise LispRuntimeError('with does not take an arg3; %s passed.' % repr(pair.right))

        # actually build the LispFunction object:
        return UserLispFunction(argbindings, functionbody)


class PutsFunction(LispFunction):
    @staticmethod
    def execute(pair, context):
        value = peval(pair.left, context)
        print(repr(value))
        return NIL()


lib = {
    'bind': BindFunction(),
    'with': WithFunction(),
    'puts': PutsFunction(),
    # 'gets': GetsFunction(),
    # 'eval': EvalFunction(),
    # 'cons': ConsFunction(),
    # 'car': CarFunction(),
    # 'cdr': CdrFunction(),
    # '+': PlusFunction(),
    # '-': MinusFunction(),
    # '*': MultiplyFunction(),
    # '/': DivideFunction(),
    # '%': ModuloFunction(),
    # '.': ConcatinateFunction(),
    # 'pos': PositionFunction(),
    # 'if': IfFunction(),
    # 'or': OrFunction(),
    # 'and': AndFunction(),
    # '>': GreaterThanFunction(),
    # '<': LessThanFunction(),
    # '=': EqualFunction(),
    # '==': IndenticalFunction()
}

# math = {
#     'sin': SinFunction(),
#     'cos': CosFunction(),
#     'tan': TanFunction(),
#     'asin': AsinFunction(),
#     'acos': AcosFunction(),
#     'atan': AtanFunction(),
#     'atan2': Atan2Function(),
#     'ln': LnFunction(),
#     'log2': Log2Function(),
#     'log10': Log10Function()
# }

def run(program):
    outer_context = Context(lib)

    UserLispFunction(NIL(), program).execute(NIL(), outer_context)


if __name__ == "__main__":
    import pycatch
    pycatch.enable(ipython=True)

    import sys
    parse_only = sys.argv[1:] and sys.argv[1] == '-p'

    possible_fn = 1
    if parse_only:
        possible_fn = 2

    source = None

    try:
        if sys.argv[1:]:
            fn = sys.argv[possible_fn]
            source = open(fn, 'r').read()
    except IndexError:
        pass

    if source is None:
        source = '\n'.join([line for line in fileinput.input()])
    
    program = parse(source)

    if parse_only:
        print("parsed stdin successfully. program:")
        cursor = program
        while type(cursor) is not NIL:
            print(repr(cursor.left))
            cursor = cursor.right
        exit(0)

    run(program)

