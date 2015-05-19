from __future__ import print_function, division

from values import NIL, MinimalispType, Symbol, Value, Pair

from parse import parse_token_prompt

from operator import mul


class LispRuntimeError(BaseException):
    pass


class UnboundSymbolError(LispRuntimeError):
    pass


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
                raise UnboundSymbolError("symbol %r was used unbound." % key)

        return self.parent[key]

    def __contains__(self, key):
        ret = super(Context, self).__contains__(key)

        if ret is False and self.parent is not None:
            ret = key in self.parent

        return ret


# evaluate - should be a Symbol, Value or a Pair.
def peval(context, o):
    # if object is literal:
    if isinstance(o, Value):
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
    if isinstance(o, LispFunction):
        raise LispRuntimeError("cannot evaluate a function")

    # in other cases, o must be a pair.
    if not isinstance(o, Pair):
        raise LispRuntimeError("cannot evaluate %s", o)
    pair = o

    # in which case, if we have been asked to run a function!
    # note that if
    if isinstance(pair.left, Symbol):
        try:
            function = context[pair.left]
        except KeyError:
            raise LispRuntimeError("unbound symbol %r" % pair.left)

        if not isinstance(function, LispFunction):
            raise LispRuntimeError("symbol %r is not bound to a function, but %r" % (pair.left, function))
    elif isinstance(pair.left, Pair):
        # pair.left is a pair. it is important to eval it here - this is the one context in which
        # it won't be evaled by pre_execute_impl, which only acts on arguments - and check we get a
        # function, rather than dying here.
        function = peval(context, pair.left)

        if not isinstance(function, LispFunction):
            raise LispRuntimeError("result %r cannot be executed as a function" % function)
    else:
        # pair.left is a Value, or something.
        raise LispRuntimeError("result %r cannot be executed as a function" % pair.left)

    return function.execute(context, pair.right)


def pre_execute_impl(context, arguments):
    """This function is run before ANY user or library function, and evaluates the arguments to
    be passed in. This step cannot be skipped, by anyone."""
    pair = arguments

    evaled_args = []

    while not isinstance(pair, NIL):
        evaled_args.append(peval(context, pair.left))
        pair = pair.right

    return evaled_args


def static_pre_execute(method="", minc=0, maxc=float('inf')):
    def inner_decorator(execute):
        def actual_execute(context, arguments):
            evaled_arguments = pre_execute_impl(context, arguments)
            count = len(evaled_arguments)
            if count < minc or count > maxc:
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
            if count < self.minc or count > self.maxc:
                raise LispRuntimeError("%s: incorrect number of arguments. accepts %r-%r, recieved %r." % (
                    method, self.minc, self.maxc, count))
            return execute(self, *([context] + evaled_arguments))
        return actual_execute
    return inner_decorator


def static_validate_value_type(method="", types=(object,)):
    def inner_decorator(execute):
        def actual_validate(context, *terms):
            for t in terms:
                if not isinstance(t, Value):
                    raise ValueError("%s: cannot compute with non-value %r" % (method, t))
                if not isinstance(t.v, types):
                    raise ValueError("%s: expected %r, found %r" % (method, t))

            # *args arrives as a tuple, not a list.
            return execute(*([context] + list(terms)))
        return actual_validate
    return inner_decorator


class LispFunction(MinimalispType):
    pass


class BindFunction(LispFunction):
    @staticmethod
    @static_pre_execute("BIND", 2, 2)
    def execute(context, symbol, value):
        if not isinstance(symbol, Symbol):
            raise LispRuntimeError('cannot BIND value %r to non-symbol %r' % (value, symbol))

        context[symbol] = value
        return NIL()


class WithFunction(LispFunction):
    @staticmethod
    @static_pre_execute("WITH", 2, 2)
    def execute(context, arg_bindings, function_body):
        # unwind with's arguments; two pairs.
        if not (isinstance(arg_bindings, Pair) or isinstance(arg_bindings, Symbol)):
            raise LispRuntimeError('WITH: %r is not an argument list.' % arg_bindings)

        args_as_list = False
        if isinstance(arg_bindings, Symbol):
            args_as_list = True

        if not isinstance(function_body, Pair):
            raise LispRuntimeError('WITH: %r is not a function body.' % function_body)

        if (not isinstance(function_body.left, Pair) or isinstance(function_body.right, NIL) or
            not isinstance(function_body.right.left, Pair)):
            # This is a single line function implementation, escape it appropriately:
            function_body = Pair(function_body, NIL())

        # actually build the LispFunction object:
        return UserLispFunction(arg_bindings, function_body, args_as_list=args_as_list)


class ApplyFunction(LispFunction):
    @staticmethod
    @static_pre_execute("APPLY", 2, 2)
    def execute(context, function, arguments):
        if not isinstance(function, LispFunction):
            raise LispRuntimeError('APPLY: first argument to apply must be a function, recieved %r' % function)

        if not isinstance(arguments, Pair):
            raise LispRuntimeError('APPLY: second argument to apply must be a list of arguments, recieved %r' % arguments)

        function.execute(context, arguments)


class EvalFunction(LispFunction):
    @staticmethod
    @static_pre_execute("EVAL", 1, 1)
    def execute(context, o):
        retval = NIL()

        # check for a list of instructions:
        if isinstance(o, Pair) and isinstance(o.left, Pair):
            pair = o
            while not isinstance(pair, NIL):
                retval = peval(context, pair.left)
                pair = pair.right
        else:
            retval = peval(context, o)

        return retval


class PutsFunction(LispFunction):
    @staticmethod
    @static_pre_execute("PUTS")
    def execute(context, *values):
        print("".join([repr(value) for value in values]))
        return NIL()


class GetsFunction(LispFunction):
    @staticmethod
    @static_pre_execute("GETS", 0)
    def execute(context, *symbols_to_bind):
        # if called with no arguments, returns a single gets.
        if len(symbols_to_bind) == 0:
            return parse_token_prompt(raw_input(">"))

        # with arguments, binds N gets' to them.
        for s in symbols_to_bind:
            if not isinstance(s, Symbol):
                raise LispRuntimeError("GETS: cannot bind to non-symbol %r." % s)

            context[s] = parse_token_prompt(raw_input("%s>" % repr(s)))

        return NIL()


class ConsFunction(LispFunction):
    @staticmethod
    @static_pre_execute("CONS", 2, 2)
    def execute(context, left, right):
        return Pair(left, right)


class CarFunction(LispFunction):
    @staticmethod
    @static_pre_execute("CAR", 1, 1)
    def execute(context, pair):
        if not isinstance(pair, Pair):
            raise LispRuntimeError('CAR: %r is not a pair.' % pair)

        return pair.left


class CdrFunction(LispFunction):
    @staticmethod
    @static_pre_execute("CDR", 1, 1)
    def execute(context, pair):
        if not isinstance(pair, Pair):
            raise LispRuntimeError('CDR: %r is not a pair.' % pair)

        return pair.right

# numeric functions use the static_validate_value_type decorator:
numbers = (int, long, float)
integers = (int, long)
floats = (float,)
strings = (str, unicode)

class PlusFunction(LispFunction):
    @staticmethod
    @static_pre_execute("+")
    @static_validate_value_type("+", numbers)
    def execute(context, *terms):
        return Value(sum([i.v for i in terms]), actual=True)


class MinusFunction(LispFunction):
    @staticmethod
    @static_pre_execute("-", 1)
    @static_validate_value_type("-", numbers)
    def execute(context, *terms):
        return Value(terms[0].v - sum([i.v for i in terms[1:]]), actual=True)


class MultiplyFunction(LispFunction):
    @staticmethod
    @static_pre_execute("*")
    @static_validate_value_type("*", numbers)
    def execute(context, *terms):
        return Value(reduce(mul, [i.v for i in terms], 1), actual=True)


class DivideFunction(LispFunction):
    @staticmethod
    @static_pre_execute("/", 1)
    @static_validate_value_type("/", numbers)
    def execute(context, *terms):
        # We use python 3's "true division", which gives floats for two int arguments.
        return Value(terms[0].v / reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


class IntegerDivideFunction(LispFunction):
    @staticmethod
    @static_pre_execute("i/", 1)
    @static_validate_value_type("i/", integers)
    def execute(context, *terms):
        return Value(terms[0].v // reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


class ModuloFunction(LispFunction):
    @staticmethod
    @static_pre_execute("%", 2)
    @static_validate_value_type("%", integers)
    def execute(context, *terms):
        return Value(terms[0].v % reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


class ConcatinateFunction(LispFunction):
    @staticmethod
    @static_pre_execute(".")
    @static_validate_value_type(".", strings)
    def execute(context, *terms):
        return Value("".join(terms), actual=True)


# Logical Functions:
# By convention we use NIL as false, as well as using 0, the empty string and  unbound Symbols
# likewise. Thus, any other numeric value is true, as is a string, Pair or bound Symbol.
# We must choose a value to return from logical comparisons. The value that was compared is not
# sufficient, since this breaks (== 0 x), and so on. We also do not want to introduce another type
# (boolean) when we only want True but not False.
# So, we choose to return Value(1, actual=True). This means we can (+ test test2 test3) and see how
# many passed, among other things.

class IfFunction(LispFunction):
    @staticmethod
    @static_pre_execute("IF", 2, 3)
    def execute(context, test, then_do, else_do=None):
        retvalue = NIL()

        if (isinstance(test, Pair) or
            (isinstance(test, Symbol) and test in context) or
            (isinstance(test, Value) and test.v)):
            retvalue = peval(context, then_do)
        elif else_do:
            retvalue = peval(context, else_do)

        return retvalue


class UserLispFunction(LispFunction):
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

    @instance_pre_execute("(user function)")
    def execute(self, outer_context, *ap):
        # initialise a new context, with arguments bound to names specified (or NIL if none passed):
        context = Context(parent=outer_context)
        ab = self.argbindings

        # bind the arguments passed:
        if self.args_as_list:
            context[ab] = ap
        else:
            for i, arg_passed in enumerate(ap):
                # instance_pre_execute should have checked we don't have too many args passed.
                arg_binding = ab[i]
                context[arg_binding] = arg_passed

        # eval the function body! We don't use EvalFunction.execute directly
        fb = self.functionbody
        retval = NIL()
        while type(fb) is not NIL:
            retval = peval(context, fb.left)
            fb = fb.right

        return retval


lib = {
    Symbol('bind'): BindFunction(),
    Symbol('with'): WithFunction(),
    Symbol('apply'): ApplyFunction(),
    Symbol('eval'): EvalFunction(),
    Symbol('puts'): PutsFunction(),
    Symbol('gets'): GetsFunction(),
    Symbol('cons'): ConsFunction(),
    Symbol('car'): CarFunction(),
    Symbol('cdr'): CdrFunction(),
    Symbol('+'): PlusFunction(),
    Symbol('-'): MinusFunction(),
    Symbol('*'): MultiplyFunction(),
    Symbol('/'): DivideFunction(),
    Symbol('i/'): IntegerDivideFunction(),
    Symbol('%'): ModuloFunction(),
    Symbol('.'): ConcatinateFunction(),
    Symbol('if'): IfFunction(),
    # Symbol('>'): GreaterThanFunction(),
    # Symbol('<'): LessThanFunction(),
    # Symbol('='): EqualFunction(),
    # Symbol('=='): IndenticalFunction()
}

# math = {
#     Symbol('sin'): SinFunction(),
#     Symbol('cos'): CosFunction(),
#     Symbol('tan'): TanFunction(),
#     Symbol('asin'): AsinFunction(),
#     Symbol('acos'): AcosFunction(),
#     Symbol('atan'): AtanFunction(),
#     Symbol('atan2'): Atan2Function(),
#     Symbol('ln'): LnFunction(),
#     Symbol('log2'): Log2Function(),
#     Symbol('log10'): Log10Function()
# }

def run(program):
    outer_context = Context(lib)

    UserLispFunction(NIL(), program).execute(outer_context, NIL())
