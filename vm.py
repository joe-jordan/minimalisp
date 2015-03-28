from __future__ import print_function

from values import NIL, MinimalispType, Symbol, Value, Pair

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
    # note that if pair.left is a pair, it is important to eval it and check we get a function, rather than dying here.
    if not isinstance(pair.left, Symbol):
        raise LispRuntimeError("not a symbol %s" % pair.left)

    try:
        function = context[pair.left]
    except KeyError:
        raise LispRuntimeError("unbound symbol %s" % pair.left)

    if not isinstance(function, LispFunction):
        raise LispRuntimeError("symbol %s is not bound to a function, but %s" % (repr(pair.left), repr(function)))

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
        while type(fb) is not NIL:
            retval = peval(fb.left, context)
            fb = fb.right

        return retval


class BindFunction(LispFunction):
    @staticmethod
    def execute(pair, context):
        if not isinstance(pair.left, Symbol):
            raise LispRuntimeError('cannot bind value %s to non-symbol %s' % (repr(pair.right), repr(pair.left)))
        # we haven't done any of the fancy argument retrieval, so just pair.right.left will have to do
        # for this hard-coded number of arguments.
        context[pair.left] = peval(pair.right.left, context)
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
    Symbol('bind'): BindFunction(),
    Symbol('with'): WithFunction(),
    Symbol('puts'): PutsFunction(),
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