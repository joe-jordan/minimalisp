from __future__ import print_function, division

from values import NIL, MinimalispType, Symbol, Value, Pair

from parse import parse_token_prompt

from operator import mul

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
    if isinstance(o, Value) or (isinstance(o, Pair) and o.quoted):
        return o

    # if object is a bound symbol, substitute its value:
    if isinstance(o, Symbol):
        if o.quoted:
            return o
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
        # pair.left is a pair, it is important to eval it and check we get a function, rather than dying here.
        function = peval(pair.left, context)

        if not isinstance(function, LispFunction):
            raise LispRuntimeError("result %r cannot be executed as a function" % function)

    return function.execute(pair.right, context)


class LispFunction(MinimalispType):
    pass


class UserLispFunction(LispFunction):
    def __init__(self, argbindings, functionbody):
        self.argbindings = argbindings

        # functionbody should be copied into a new head pair, minus the quoted status.
        self.functionbody = Pair(functionbody.left, functionbody.right)

    def execute(self, ap, outer_context):
        # initialise a new context, with arguments bound to names specified (or NIL if none passed):
        context = Context(parent=outer_context)
        ab = self.argbindings
        while type(ab) is not NIL:
            try:
                if isinstance(ap.left, Symbol) and not ap.left.quoted:
                    context[ab.left] = context[ap.left]
                else:
                    context[ab.left] = ap.left
            except AttributeError:
                context[ab.left] = NIL()
            except KeyError:
                raise ValueError("cannot bind argument %r which is unbound in outer scope." % ap.left)
            ab = ab.right
            try:
                ap = ap.right
            except AttributeError:
                pass

        # eval each line of code in the function:
        fb = self.functionbody
        retval = NIL()
        while type(fb) is not NIL:
            retval = peval(fb.left, context)
            fb = fb.right

        return retval


class BindFunction(LispFunction):
    @staticmethod
    def execute(pair, context):
        if not isinstance(pair.left, Symbol):
            raise LispRuntimeError('cannot bind value %r to non-symbol %r' % (pair.right.left, pair.left))
        # we haven't done any of the fancy argument retrieval, so just pair.right.left will have to do
        # for this hard-coded number of arguments.
        context[pair.left] = peval(pair.right.left, context)
        return NIL()


class WithFunction(LispFunction):
    @staticmethod
    def execute(pair, context):
        # unwind with's arguments; two quoted pairs.
        argbindings = pair.left
        if not isinstance(argbindings, Pair) or not argbindings.quoted:
            raise LispRuntimeError('with arg1 not satisfied, %r is not a quoted list.' % argbindings)

        pair = pair.right
        functionbody = pair.left
        if not isinstance(functionbody, Pair) or not functionbody.quoted:
            raise LispRuntimeError('with arg2 not satisfied, %r is not a quoted list.' % functionbody)

        if not isinstance(pair.right, NIL):
            raise LispRuntimeError('with does not take an arg3; %r passed.' % pair.right)

        # actually build the LispFunction object:
        return UserLispFunction(argbindings, functionbody)


class PutsFunction(LispFunction):
    @staticmethod
    def execute(pair, context):
        values = [peval(pair.left, context)]
        while not isinstance(pair.right, NIL):
            pair = pair.right
            values.append(peval(pair.left, context))
        print("".join([repr(value) for value in values]))
        return NIL()


class GetsFunction(LispFunction):
    @staticmethod
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
            assert isinstance(s, Symbol), "GETS: cannot bind to non-symbol %r." % s

            context[s] = parse_token_prompt(raw_input("%s>" % repr(s)))

        return NIL()


class NoArgumentsPassedError(BaseException):
    pass


class NonValueError(BaseException):
    def __init__(self, *args, **kwargs):
        self.t = kwargs.pop('t')
        super(NonValueError, self).__init__(*args, **kwargs)


class ValueFunction(LispFunction):
    @staticmethod
    def execute(pair, context):
        terms = []
        while not isinstance(pair, NIL):
            terms.append(peval(pair.left, context))
            pair = pair.right

        if not terms:
            raise NoArgumentsPassedError()

        for t in terms:
            if not isinstance(t, Value):
                raise NonValueError(t=t)

        return terms


class PlusFunction(ValueFunction):
    @staticmethod
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

        # We use python 3's "true division", which gives floats for two int arguments.
        return Value(terms[0].v // reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


class ModuloFunction(ValueFunction):
    @staticmethod
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

        # We use python 3's "true division", which gives floats for two int arguments.
        return Value(terms[0].v % reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


class ConcatinateFunction(ValueFunction):
    @staticmethod
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

        # We use python 3's "true division", which gives floats for two int arguments.
        return Value(terms[0].v % reduce(mul, [i.v for i in terms[1:]], 1), actual=True)


lib = {
    Symbol('bind'): BindFunction(),
    Symbol('with'): WithFunction(),
    Symbol('puts'): PutsFunction(),
    Symbol('gets'): GetsFunction(),
    # Symbol('eval'): EvalFunction(),
    # Symbol('cons'): ConsFunction(),
    # Symbol('car'): CarFunction(),
    # Symbol('cdr'): CdrFunction(),
    Symbol('+'): PlusFunction(),
    Symbol('-'): MinusFunction(),
    Symbol('*'): MultiplyFunction(),
    Symbol('/'): DivideFunction(),
    Symbol('i/'): IntegerDivideFunction(),
    Symbol('%'): ModuloFunction(),
    # Symbol('.'): ConcatinateFunction(),
    # Symbol('pos'): PositionFunction(),
    # Symbol('if'): IfFunction(),
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
