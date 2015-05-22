from __future__ import print_function, division

import math

from values import Value, Symbol
from vm import LispFunction, numbers, pre_execute_impl


def class_pre_execute(minc=0, maxc=float('inf')):
    def inner_decorator(execute):
        def actual_execute(cls, context, arguments):
            evaled_arguments = pre_execute_impl(context, arguments)
            count = len(evaled_arguments)
            if count < minc or count > maxc:
                raise LispRuntimeError("%s: incorrect number of arguments. accepts %r-%r, recieved %r." % (
                    cls.name, minc, maxc, count))
            return execute(*([cls, context] + evaled_arguments))
        return actual_execute
    return inner_decorator


def class_validate_value_type(types=(object,)):
    def inner_decorator(execute):
        def actual_validate(cls, context, *terms):
            for t in terms:
                if not isinstance(t, Value):
                    raise ValueError("%s: cannot compute with non-value %r" % (cls.name, t))
                if not isinstance(t.v, types):
                    raise ValueError("%s: expected %r, found %r" % (cls.name, t))

            # *args arrives as a tuple, not a list.
            return execute(*([cls, context] + list(terms)))
        return actual_validate
    return inner_decorator


class MathFunctionOneArg(LispFunction):
    name = None
    @classmethod
    @class_pre_execute(1, 1)
    @class_validate_value_type(numbers)
    def execute(cls, context, x):
        return Value(cls.impl(x.v), actual=True)


class SinFunction(MathFunctionOneArg):
    name = "SIN"
    impl = math.sin


class CosFunction(MathFunctionOneArg):
    name = "COS"
    impl = math.cos


class TanFunction(MathFunctionOneArg):
    name = "TAN"
    impl = math.tan


class AsinFunction(MathFunctionOneArg):
    name = "ASIN"
    impl = math.asin


class AcosFunction(MathFunctionOneArg):
    name = "ACOS"
    impl = math.acos


class AtanFunction(MathFunctionOneArg):
    name = "ATAN"
    impl = math.atan


class ExpFunction(MathFunctionOneArg):
    name = "EXP"
    impl = math.exp


# we use default base 10, but allow an optional second argument to override.
class LogFunction(LispFunction):
    name = "LOG"
    @classmethod
    @class_pre_execute(1, 2)
    @class_validate_value_type(numbers)
    def execute(cls, context, a, b=Value(10, actual=True)):
        return Value(math.log(a.v, b.v), actual=True)


class Atan2Function(LispFunction):
    name = "ATAN2"
    @classmethod
    @class_pre_execute(2, 2)
    @class_validate_value_type(numbers)
    def execute(cls, context, a, b):
        return Value(math.atan2(a.v, b.v), actual=True)


maths_functions = {
    Symbol('sin'): SinFunction(),
    Symbol('cos'): CosFunction(),
    Symbol('tan'): TanFunction(),
    Symbol('asin'): AsinFunction(),
    Symbol('acos'): AcosFunction(),
    Symbol('atan'): AtanFunction(),
    Symbol('atan2'): Atan2Function(),
    Symbol('log'): LogFunction(),
    Symbol('pi'): Value(math.pi, actual=True),
    Symbol('exp'): ExpFunction()
}
