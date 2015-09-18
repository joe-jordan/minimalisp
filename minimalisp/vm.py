from __future__ import print_function, division

from values import NIL, LispType, LispValue, Symbol, Value, Pair

from parse import parse_token_prompt

from operator import mul

import random
random.seed()

# overwritten in the executible
PERMISSIVE = False


class LispRuntimeError(BaseException):
    pass


class UnboundSymbolError(LispRuntimeError):
    pass

def sexpr_from_iterator(it):
    pair = NIL()
    for i in reversed(it):
        pair = Pair(i, pair)

    return pair


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
                if PERMISSIVE:
                    return NIL()
                raise UnboundSymbolError("symbol %r was used unbound." % key)

        return self.parent[key]

    def __contains__(self, key):
        ret = super(Context, self).__contains__(key)

        if ret is False and self.parent is not None:
            ret = key in self.parent

        return ret


# evaluate - should be a Symbol, Value or a Pair.
def peval(context, o):
    if not isinstance(o, LispType):
        raise LispRuntimeError("peval was passed %r, which is not a LispType instance." % o)

    # Value's and NIL
    if isinstance(o, LispValue):
        return o

    # if object is quoted, un-quote it:
    if isinstance(o, Pair) and o.quoted:
        return Pair(o.left, o.right)
    if isinstance(o, Symbol) and o.quoted:
        return Symbol(o.s)

    # if object is a bound symbol, substitute its value:
    if isinstance(o, Symbol):
        return context[o]

    # if o is a function:
    if hasattr(o, '__call__'):
        raise LispRuntimeError("cannot evaluate a function")

    # in other cases, o must be a pair.
    if not isinstance(o, Pair):
        raise LispRuntimeError("cannot evaluate %s", o)
    pair = o

    # in which case, if we have been asked to run a function!
    if isinstance(pair.left, Symbol):
        try:
            function = context[pair.left]
        except KeyError:
            raise LispRuntimeError("unbound symbol %r" % pair.left)

        if not hasattr(function, '__call__'):
            raise LispRuntimeError("symbol %r is not bound to a function, but %r" % (pair.left, function))
    elif isinstance(pair.left, Pair):
        # pair.left is a pair. it is important to eval it here - this is the one context in which
        # it won't be evaled by pre_execute_impl, which only acts on arguments - and check we get a
        # function, rather than dying here.
        function = peval(context, pair.left)

        if not hasattr(function, '__call__'):
            raise LispRuntimeError("result %r cannot be executed as a function" % function)
    elif hasattr(pair.left, '__call__'):
        # someone has got a function object in the right place for us. Go them!
        function = pair.left
    else:
        # pair.left is a Value, or something.
        raise LispRuntimeError("result %r cannot be executed as a function" % pair.left)

    return function(context, pair.right)


def pre_execute_impl(context, arguments):
    """This function is run before ANY user or library function, and evaluates the arguments to
    be passed in. This step cannot be skipped, by anyone."""
    pair = arguments

    evaled_args = []

    while not isinstance(pair, NIL):
        evaled_args.append(peval(context, pair.left))
        pair = pair.right

    return evaled_args


def pre_execute(method="", minc=0, maxc=float('inf')):
    def inner_decorator(execute):
        def actual_execute(context, arguments):
            evaled_arguments = pre_execute_impl(context, arguments)
            count = len(evaled_arguments)
            if not PERMISSIVE and (count < minc or count > maxc):
                raise LispRuntimeError("%s: incorrect number of arguments. accepts %r-%r, recieved %r." % (
                    method, minc, maxc, count))
            return execute(*([context] + evaled_arguments))
        return actual_execute
    return inner_decorator


def instance_pre_execute(method=""):
    def inner_decorator(execute):
        def actual_execute(self, context, arguments):
            evaled_arguments = pre_execute_impl(context, arguments)
            count = len(evaled_arguments)
            if not PERMISSIVE and (count < self.minc or count > self.maxc):
                raise LispRuntimeError("%s: incorrect number of arguments. accepts %r-%r, recieved %r." % (
                    method, self.minc, self.maxc, count))
            return execute(self, *([context] + evaled_arguments))
        return actual_execute
    return inner_decorator


# numeric functions use the static_validate_value_type decorator:
numbers = (int, long, float)
integers = (int, long)
floats = (float,)
strings = (str, unicode)
values = numbers + strings


def static_validate_value_type(method="", types=(object,)):
    def inner_decorator(execute):
        def actual_validate(context, *terms):
            for t in terms:
                if not isinstance(t, Value):
                    raise ValueError("%s: cannot compute with non-value %r" % (method, t))
                if not isinstance(t.v, types):
                    raise ValueError("%s: expected %r, found %r" % (method, types, t))

            # *args arrives as a tuple, not a list.
            return execute(*([context] + list(terms)))
        return actual_validate
    return inner_decorator


@pre_execute("BIND", 2, 2)
def bind(context, symbol=None, value=NIL(), *args):
    if not isinstance(symbol, Symbol):
        if not PERMISSIVE:
            raise LispRuntimeError('cannot BIND value %r to non-symbol %r' % (value, symbol))
    else:
        context[symbol] = value

    return NIL()


def noop(*args):
    pass


@pre_execute("WITH", 2)
def _with(context, arg_bindings=NIL(), *lines_of_function_body):
    # unwind with's arguments; two pairs.
    args_as_list = False
    if not (isinstance(arg_bindings, Pair) or isinstance(arg_bindings, Symbol)):
        if not PERMISSIVE:
            raise LispRuntimeError('WITH: %r is not an argument list.' % arg_bindings)
    else:
        if isinstance(arg_bindings, Symbol):
            args_as_list = True

    if not lines_of_function_body:
        if PERMISSIVE:
            return noop
        else:
            raise LispRuntimeError('WITH: cannot define an empty function.')

    # actually build the LispFunction object:
    return UserLispFunction(arg_bindings, lines_of_function_body, args_as_list=args_as_list)


@pre_execute("EVAL", 1)
def _eval(context, *lines):
    retval = NIL()

    for l in lines:
        retval = peval(context, l)

    return retval


@pre_execute("PUTS")
def puts(context, *values):
    if not PERMISSIVE and any([
        not isinstance(v, (Value, Pair, Symbol, NIL)) and not hasattr(v, '__call__') for v in values
    ]):
        raise LispRuntimeError("expected lisp objects, got %s" % repr(values))
    print("".join([repr(value) for value in values]))
    return NIL()


@pre_execute("GETS", 0)
def gets(context, *symbols_to_bind):
    # if called with no arguments, returns a single gets.
    if len(symbols_to_bind) == 0:
        return parse_token_prompt(raw_input(">"))

    # with arguments, binds N gets' to them.
    for s in symbols_to_bind:
        if not isinstance(s, Symbol):
            if not PERMISSIVE:
                raise LispRuntimeError("GETS: cannot bind to non-symbol %r." % s)
        else:
            context[s] = parse_token_prompt(raw_input("%s>" % repr(s)))

    return NIL()


@pre_execute("CONS", 2, 2)
def cons(context, left=NIL(), right=NIL(), *args):
    return Pair(left, right)


@pre_execute("CAR", 1, 1)
def car(context, pair=NIL(), *args):
    if not isinstance(pair, Pair):
        if PERMISSIVE:
            return pair
        raise LispRuntimeError('CAR: %r is not a pair.' % pair)

    return pair.left


@pre_execute("CDR", 1, 1)
def cdr(context, pair=NIL(), *args):
    if not isinstance(pair, Pair):
        if PERMISSIVE:
            return pair
        raise LispRuntimeError('CDR: %r is not a pair.' % pair)

    return pair.right


@pre_execute("+")
@static_validate_value_type("+", numbers)
def plus(context, *terms):
    return Value(sum([i.v for i in terms]), actual=True)


@pre_execute("-", 1)
@static_validate_value_type("-", numbers)
def minus(context, *terms):
    return Value(terms[0].v - sum([i.v for i in terms[1:]]), actual=True)


@pre_execute("*")
@static_validate_value_type("*", numbers)
def multiply(context, *terms):
    return Value(reduce(mul, [i.v for i in terms], 1), actual=True)


@pre_execute("/", 1)
@static_validate_value_type("/", numbers)
def divide(context, *terms):
    # We use python 3's "true division", which gives floats for two int arguments.
    return Value(terms[0].v / reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


@pre_execute("i/", 1)
@static_validate_value_type("i/", integers)
def idivide(context, *terms):
    return Value(terms[0].v // reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


@pre_execute("%", 2)
@static_validate_value_type("%", integers)
def modulo(context, *terms):
    return Value(terms[0].v % reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


@pre_execute("ROUND", 1, 1)
@static_validate_value_type("ROUND", floats)
def _round(context, f):
    return Value(int(round(f.v)), actual=True)


@pre_execute(".")
@static_validate_value_type(".", strings)
def concatinate(context, *terms):
    return Value("".join(terms), actual=True)


@pre_execute('SPLIT', 1, 2)
@static_validate_value_type('SPLIT', strings)
def split(context, input, substring=None):
    retvalue = NIL()

    args = []
    if substring:
        args.append(substring)

    for tok in reversed(input.v.split(*args)):
        retvalue = Pair(Value(tok, actual=True), retvalue)

    return retvalue


@pre_execute("RAND", 0, 0)
def rand(context):
    return Value(random.random(), actual=True)


# Logical Functions:
# By convention we use NIL as false, as well as using 0, the empty string and unbound Symbols
# likewise. Thus, any other numeric value is true, as is a string, Pair or bound Symbol.
# We must choose a value to return from logical comparisons. The value that was compared is not
# sufficient, since this breaks (== 0 x), and so on. We also do not want to introduce another type
# (boolean) when we only want True but not False.
# So, we choose to return Value(1, actual=True). This means we can (+ test test2 test3) and see how
# many passed, among other things.

@pre_execute("IF", 2, 3)
def _if(context, test, then_do, else_do=None):
    retvalue = NIL()

    if (isinstance(test, Pair) or
        (isinstance(test, Symbol) and test in context) or
        (isinstance(test, Value) and test.v)):
        retvalue = peval(context, then_do)
    elif else_do:
        retvalue = peval(context, else_do)

    return retvalue


@pre_execute("=", 2)
def equal(context, *terms):
    retvalue = Value(1, actual=True)
    lvalue = terms[0]

    for rvalue in terms[1:]:
        if lvalue != rvalue:
            retvalue = NIL()
            break

    return retvalue


@pre_execute("==", 2)
def identical(context, *terms):
    """This function is not very useful, I think, but can't possibly be implemented in the language
    without a minimalisp version of python's `id`, which is even worse."""
    retvalue = Value(1, actual=True)
    lvalue = terms[0]

    for rvalue in terms[1:]:
        if id(lvalue) != id(rvalue):
            retvalue = NIL()
            break

    return retvalue


@pre_execute(">", 2)
@static_validate_value_type(">", values)
def greater_than(context, *terms):
    retvalue = Value(1, actual=True)
    lvalue = terms[0]

    for rvalue in terms[1:]:
        if lvalue.v <= rvalue.v:
            retvalue = NIL()
            break

    return retvalue


@pre_execute("<", 2)
@static_validate_value_type("<", values)
def less_than(context, *terms):
    retvalue = Value(1, actual=True)
    lvalue = terms[0]

    for rvalue in terms[1:]:
        if lvalue.v >= rvalue.v:
            retvalue = NIL()
            break

    return retvalue


@pre_execute("DOWHILE", 1)
def dowhile(context, *body):
    """works like EVAL, except it repeats the function body again and again until its return
    value is NIL or 0. Always returns NIL, but leaks bindings."""
    result = NIL()

    for line in body:
        result = peval(context, line)

    while (isinstance(result, Pair) or
        (isinstance(result, Symbol) and result in context) or
        (isinstance(result, Value) and result.v)):

        for line in body:
            result = peval(context, line)

    return NIL()


class UserLispFunction(object):
    def __init__(self, argbindings, functionbody, args_as_list=False):
        # both are unquoted pairs, which WITH will check for us.
        self.args_as_list = args_as_list
        self.argbindings = argbindings
        self.functionbody = functionbody
        self.minc = 0

        if args_as_list:
            # a list of arguments may be arbitrarily long.
            self.maxc = float('inf')
        else:
            # find out how long argbindings is:
            args = []
            sargs = argbindings
            while not isinstance(sargs, NIL):
                args.append(sargs.left)
                sargs = sargs.right
            self.maxc = len(args)

            self.argbindings = args

    def __repr__(self):
        return "(user function)"

    @instance_pre_execute("(user function)")
    def __call__(self, outer_context, *ap):
        # initialise a new context, with arguments bound to names specified (or NIL if none passed):
        context = Context(parent=outer_context)
        ab = self.argbindings

        # bind the arguments passed:
        if self.args_as_list:
            context[ab] = sexpr_from_iterator(ap)
        else:
            for i, arg_passed in enumerate(ap):
                # instance_pre_execute should have checked we don't have too many args passed.
                arg_binding = ab[i]
                context[arg_binding] = arg_passed

        retval = NIL()
        for line in self.functionbody:
            retval = peval(context, line)

        self.last_execute_context = context

        return retval


lib = {
    Symbol('bind'): bind,
    Symbol('with'): _with,
    Symbol('eval'): _eval,
    Symbol('puts'): puts,
    Symbol('gets'): gets,
    Symbol('cons'): cons,
    Symbol('car'): car,
    Symbol('cdr'): cdr,
    Symbol('+'): plus,
    Symbol('-'): minus,
    Symbol('*'): multiply,
    Symbol('/'): divide,
    Symbol('i/'): idivide,
    Symbol('%'): modulo,
    Symbol('round'): _round,
    Symbol('.'): concatinate,
    Symbol('split'): split,
    Symbol('rand'): rand,
    Symbol('if'): _if,
    Symbol('>'): greater_than,
    Symbol('<'): less_than,
    Symbol('='): equal,
    Symbol('=='): identical,
    Symbol('dowhile'): dowhile
}


def run(program, use_stdlib=False, with_math=False):
    outer_context = Context(lib)

    if use_stdlib:
        stdlib_program = use_stdlib

        stdlib = UserLispFunction(NIL(), stdlib_program)

        stdlib(outer_context, NIL())

        outer_context = stdlib.last_execute_context

    if with_math:
        import maths
        outer_context.update(maths.maths_functions)

    UserLispFunction(NIL(), program)(outer_context, NIL())
