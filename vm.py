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
def peval(o, context):
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
        function = peval(pair.left, context)

        if not isinstance(function, LispFunction):
            raise LispRuntimeError("result %r cannot be executed as a function" % function)
    else:
        # pair.left is a Value, or something.
        raise LispRuntimeError("result %r cannot be executed as a function" % pair.left)

    return function.execute(pair.right, context)


def pre_execute_impl(arguments, context):
    """This function is run before ANY user or library function, and evaluates the arguments to
    be passed in. This step cannot be skipped, by anyone."""
    pair = arguments

    evaled_args = []

    while not isinstance(pair, NIL):
        evaled_args.append(peval(pair.left, context))
        pair = pair.right

    output = NIL()
    for arg in reversed(evaled_args):
        output = Pair(arg, output)

    return output


def static_pre_execute(execute):
    def actual_execute(arguments, context):
        evaled_arguments = pre_execute_impl(arguments, context)
        return execute(evaled_arguments, context)
    return actual_execute


def instance_pre_execute(execute):
    def actual_execute(self, arguments, context):
        evaled_arguments = pre_execute_impl(arguments, context)
        return execute(self, evaled_arguments, context)
    return actual_execute


class LispFunction(MinimalispType):
    pass


class BindFunction(LispFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        if not isinstance(pair.left, Symbol):
            raise LispRuntimeError('cannot BIND value %r to non-symbol %r' % (pair.right.left, pair.left))
        # we haven't done any of the fancy argument retrieval, so just pair.right.left will have to do
        # for this hard-coded number of arguments.
        context[pair.left] = pair.right.left
        return NIL()


class WithFunction(LispFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        # unwind with's arguments; two pairs.
        argbindings = pair.left
        if not isinstance(argbindings, Pair):
            raise LispRuntimeError('WITH: input arguments not satisfied, %r is not an argument list.' % argbindings)

        pair = pair.right
        functionbody = pair.left
        if not isinstance(functionbody, Pair):
            raise LispRuntimeError('WITH: function body argument not satisfied, %r is not a function body list.' % functionbody)

        if (not isinstance(functionbody.left, Pair) or isinstance(functionbody.right, NIL) or
            not isinstance(functionbody.right.left, Pair)):
            # This is a single line function implementation, escape it appropriately:
            functionbody = Pair(functionbody, NIL())

        if not isinstance(pair.right, NIL):
            raise LispRuntimeError('WITH does not take a third argument; %r passed.' % pair.right)

        # actually build the LispFunction object:
        return UserLispFunction(argbindings, functionbody)


class EvalFunction(LispFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        # no fuss, this method does what it says on the tin.
        retval = NIL()

        # check for a list of instructions:
        if isinstance(pair.left, Pair) and isinstance(pair.right, NIL):
            pair = pair.left

        while not isinstance(pair, NIL):
            retval = peval(pair.left, context)
            pair = pair.right

        return retval


class PutsFunction(LispFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        values = [pair.left]
        while not isinstance(pair.right, NIL):
            pair = pair.right
            values.append(pair.left)
        print("".join([repr(value) for value in values]))
        return NIL()


class GetsFunction(LispFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        # if called with no arguments, returns a single gets.
        if isinstance(pair.left, NIL):
            return parse_token_prompt(raw_input(">"))

        # with arguments, binds N gets' to them.
        symbols_to_bind = [pair.left]
        while not isinstance(pair.right, NIL):
            pair = pair.right
            symbols_to_bind.append(pair.left)

        for s in symbols_to_bind:
            if not isinstance(s, Symbol):
                raise LispRuntimeError("GETS: cannot bind to non-symbol %r." % s)

            context[s] = parse_token_prompt(raw_input("%s>" % repr(s)))

        return NIL()


class ConsFunction(LispFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        left = pair.left

        if isinstance(pair.right, NIL):
            raise LispRuntimeError("CONS: two arguments are required, only recieved one (%r)" % left)

        pair = pair.right
        right = pair.left

        if not isinstance(pair.right, NIL):
            raise LispRuntimeError("CONS: two arguments are required, recieved three: %r, %r, %r" % left, right, pair.right)

        return Pair(left, right)


class CarFunction(LispFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        return pair.left.left


class CdrFunction(LispFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        return pair.left.right


class NoArgumentsPassedError(BaseException):
    pass


class NonValueError(BaseException):
    def __init__(self, *args, **kwargs):
        self.t = kwargs.pop('t')
        super(NonValueError, self).__init__(*args, **kwargs)


class ValueFunction(LispFunction):
    # This level is abstract, all children should apply the decorator.
    @staticmethod
    def execute(pair, context):
        terms = []
        while not isinstance(pair, NIL):
            terms.append(pair.left)
            pair = pair.right

        if not terms:
            raise NoArgumentsPassedError()

        for t in terms:
            if not isinstance(t, Value):
                raise NonValueError(t=t)

        return terms


class PlusFunction(ValueFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        try:
            terms = super(PlusFunction, PlusFunction).execute(pair, context)
        except NoArgumentsPassedError:
            return Value(0, actual=True)
        except NonValueError, e:
            raise ValueError("+: cannot sum non-value %r" % e.t)

        return Value(sum([i.v for i in terms]), actual=True)


class MinusFunction(ValueFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        try:
            terms = super(MinusFunction, MinusFunction).execute(pair, context)
        except NoArgumentsPassedError:
            return Value(0, actual=True)
        except NonValueError, e:
            raise ValueError("-: cannot subtract non-value %r" % e.t)

        return Value(terms[0].v - sum([i.v for i in terms[1:]]), actual=True)


class MultiplyFunction(ValueFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        try:
            terms = super(MultiplyFunction, MultiplyFunction).execute(pair, context)
        except NoArgumentsPassedError:
            return Value(1, actual=True)
        except NonValueError, e:
            raise ValueError("*: cannot take product of non-value %r" % e.t)

        return Value(reduce(mul, [i.v for i in terms], 1), actual=True)


class DivideFunction(ValueFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        try:
            terms = super(DivideFunction, DivideFunction).execute(pair, context)
        except NoArgumentsPassedError:
            return Value(1, actual=True)
        except NonValueError, e:
            raise ValueError("/: cannot divide non-value %r" % e.t)

        # We use python 3's "true division", which gives floats for two int arguments.
        return Value(terms[0].v / reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


class IntegerDivideFunction(ValueFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        try:
            terms = super(IntegerDivideFunction, IntegerDivideFunction).execute(pair, context)
        except NoArgumentsPassedError:
            return Value(1, actual=True)
        except NonValueError, e:
            raise ValueError("i/: cannot divide non-value %r" % e.t)
        for i in terms:
            if not isinstance(i.v, (int, long)):
                raise ValueError("i/: cannot integer divide non-integer %r" % i)

        return Value(terms[0].v // reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


class ModuloFunction(ValueFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        try:
            terms = super(ModuloFunction, ModuloFunction).execute(pair, context)
        except NoArgumentsPassedError:
            return Value(1, actual=True)
        except NonValueError, e:
            raise ValueError("%: cannot modulo non-value %r" % e.t)
        for i in terms:
            if not isinstance(i.v, (int, long)):
                raise ValueError("%: cannot modulo non-integer %r" % i)

        return Value(terms[0].v % reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


class ConcatinateFunction(ValueFunction):
    @staticmethod
    @static_pre_execute
    def execute(pair, context):
        try:
            terms = super(ModuloFunction, ModuloFunction).execute(pair, context)
        except NoArgumentsPassedError:
            return Value(1, actual=True)
        except NonValueError, e:
            raise ValueError(".: cannot concatinate non-value %r" % e.t)
        for i in terms:
            if not isinstance(i.v, (str, unicode)):
                raise ValueError(".: cannot concatinate non-string %r" % i)

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
    @static_pre_execute
    def execute(pair, context):
        test = pair.left

        if not isinstance(pair.right, Pair):
            raise LispRuntimeError("IF: at least two arguments required, only recieved one (%r)" % test)

        pair = pair.right
        then_do = pair.left
        else_do = None

        if isinstance(pair.right, Pair):

            pair = pair.right
            else_do = pair.left

            if not isinstance(pair.right, NIL):
                raise LispRuntimeError("IF: maximum of three arguments accepted, recieved a fourth (%r)" % pair.right)

        retvalue = NIL()

        if (isinstance(test, Pair) or
            (isinstance(test, Symbol) and test in context) or
            (isinstance(test, Value) and test.v)):
            retvalue = peval(then_do, context)
        elif else_do:
            retvalue = peval(else_do, context)

        return retvalue


class UserLispFunction(LispFunction):
    def __init__(self, argbindings, functionbody):
        # both are unquoted pairs, which WITH will check for us.
        self.argbindings = argbindings
        self.functionbody = functionbody

    @instance_pre_execute
    def execute(self, ap, outer_context):
        # initialise a new context, with arguments bound to names specified (or NIL if none passed):
        context = Context(parent=outer_context)
        ab = self.argbindings

        while type(ab) is not NIL:
            try:
                context[ab.left] = ap.left
            except AttributeError:
                context[ab.left] = NIL()
            ab = ab.right
            try:
                ap = ap.right
            except AttributeError:
                pass

        # eval the function body! We don't use EvalFunction.execute directly
        fb = self.functionbody
        retval = NIL()
        while type(fb) is not NIL:
            retval = peval(fb.left, context)
            fb = fb.right

        return retval


lib = {
    Symbol('bind'): BindFunction(),
    Symbol('with'): WithFunction(),
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
    # Symbol('or'): OrFunction(),
    # Symbol('and'): AndFunction(),
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

    UserLispFunction(NIL(), program).execute(NIL(), outer_context)
