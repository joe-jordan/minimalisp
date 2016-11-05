from __future__ import print_function, division

import math

from values import Value, Symbol
from vm import numbers, pre_execute


def instance_validate_value_type(types=(object,)):
    def inner_decorator(execute):
        def actual_validate(self, context, *terms):
            for t in terms:
                if not isinstance(t, Value):
                    raise ValueError("%s: cannot compute with non-value %r" % (self.name, t))
                if not isinstance(t.v, types):
                    raise ValueError("%s: expected %r, found %r" % (self.name, types, t))

            # *args arrives as a tuple, not a list.
            return execute(*([self, context] + list(terms)))
        return actual_validate
    return inner_decorator


def validate_value_type(name, types=(object,)):
    def inner_decorator(execute):
        def actual_validate(context, *terms):
            for t in terms:
                if not isinstance(t, Value):
                    raise ValueError("%s: cannot compute with non-value %r" % (name, t))
                if not isinstance(t.v, types):
                    raise ValueError("%s: expected %r, found %r" % (name, types, t))

            # *args arrives as a tuple, not a list.
            return execute(*([context] + list(terms)))
        return actual_validate
    return inner_decorator


def MathFunctionOneArg(name, impl):

    @pre_execute(name, 1, 1)
    @validate_value_type(numbers)
    def math_fn(context, x):
        return Value(impl(x.v), actual=True)

    return math_fn


sin = MathFunctionOneArg("SIN", math.sin)
cos = MathFunctionOneArg("COS", math.cos)
tan = MathFunctionOneArg("TAN", math.tan)

asin = MathFunctionOneArg("ASIN", math.asin)
acos = MathFunctionOneArg("ACOS", math.acos)
atan = MathFunctionOneArg("ATAN", math.atan)

exp = MathFunctionOneArg("EXP", math.exp)


# we use default base 10, but allow an optional second argument to override.
@pre_execute("LOG", 1, 2)
@validate_value_type("LOG", numbers)
def log(context, a, b=Value(10, actual=True)):
    return Value(math.log(a.v, b.v), actual=True)


@pre_execute("ATAN", 2, 2)
@validate_value_type("ATAN", numbers)
def atan2(context, a, b):
    return Value(math.atan2(a.v, b.v), actual=True)


maths_functions = {
    Symbol('sin'): sin,
    Symbol('cos'): cos,
    Symbol('tan'): tan,
    Symbol('asin'): asin,
    Symbol('acos'): acos,
    Symbol('atan'): atan,
    Symbol('atan2'): atan2,
    Symbol('log'): log,
    Symbol('pi'): Value(math.pi, actual=True),
    Symbol('exp'): exp
}
