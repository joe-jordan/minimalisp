Notes on `'`:


####VERSION 1:

In vanilla lisps, including both common lisp and scheme, the following statement is parsed as follows:

    '(cos (- 3 1))
    => (COS . ((- . (3 . (1 . NIL))) . NIL))

That is, `(- 3 1)` is not evaluated to `2`, because of the quote on the outermost S-expression, which affects *all* sub-expressions.

This is very inflexible, since we cannot use local variable values, or the result of `cons`, in our quoted code without rewriting the entire section very verbosely:

    (cons 'cos (cons (- 3 1) NIL))
    => (COS . (2 . NIL))

We prefer a much simpler convention for mixing quoted and unquoted code, especially when we require such frequent quoting by eliminating magic functions, by having two types of quote, with two different behaviours.

First, twin-quotes (written as `''` not `"`!) which behave like vanilla lisp single quotes, and escape all sub-expressions:

    ''(cos (- 3 1))
    => (COS . ((- . (3 . (1 . NIL))) . NIL))

Secondly, single quotes, which only have scope on the level of the outer set of parentheses (whether an S-expression or a pair literal):

    '(cos (- 3 1))
    => (COS . (2 . NIL))

In this way, we can construct a quoted "function call" containing calculated values as the arguments, and indeed calculated code structure, without the extremely verbose quoting of every other expression.

For clarity, if there are additional elements in the outer quoted S-expression we consider them quoted at the first level too, not evaluated:

    '(+ (- 3 1) five)
    => (+ . (2 . (FIVE . NIL)))

The other important point to make is on a matter of great confusion for the author upon attempting to find simple equivalent expressions in other lisps - the quoting of single symbols to prevent their evaluation. If we had written the second code sample as follows, we would have got a truly useless result:

    (cons cos (cons (- 3 1) NIL))
    => (#<procedure cos> . (2 . NIL))

It must be stressed that if one calls `eval` on this expression, an error results!

Thus, the convention in minimalisp should be that unless a symbol is part of an evaluated computation, its value (whether a procedure or a value) will not be substituted, i.e. that symbols evaluate to themselves until actually part of a function call.

Thus, in minimalisp:

    (cons cos (cons (- 3 1) NIL))
    => (COS . (2 . NIL))
    ; and
    '(cos (- 3 1))
    => (COS . (2 . NIL))
    ; i.e. these are two ways of expressing the same thing.

These modifications may be confusing to an experienced lisp programmer, but those programmers should be using more advanced implementations like Common Lisp and Scheme. Minimalisp is designed for generating and evaluating genetic programs, which make heavy use of quoted expressions, and with no magic functions it requires even more quoted structures! Thus, the quoting system needs to be much more flexible than other lisps, particularly the first example. I believe that the rules proposed here will result if fewer runtime errors owing to confusion about quoting.

One final point, on nested quoting. Our double quote allows you to completely escape an S-expression structure, for example the else clause in an `if` statement. This means that one can technically have nested quoting, i.e. single or double quotes inside another double quoted structure - these would be treated as quoted when `eval` is called on them - i.e. your `if` implementations can contain quoted logic too.






####VERSION 2:

hmm. So in other lisps we have a difference between:

    '(cos 2)
    => (COS . (2 . NIL))

and 

    (cons cos (cons 2 NIL))
    => (#<procedure cos> . (2 . NIL))

which is totally broken (since if we call `eval` on the second form, we get an error rather than a float - but the code isn't evaluated immediately because of the `cons` returning a pair like `'` does.) What is happening is simply that `cos` is being substituted for its value in the second expression, while not in the first (because its quoted.) In cases of literal values this might be helpful, since it means we don't need to store local scope when `eval`ing things - If we have a local variable called `arg` that holds the value `2`, we can do:

    (cons cos (cons arg NIL))
    => (#<procedure cos> . (2 . NIL))

i.e. we store the local value immediately, rather than storing the symbol `arg` and looking up its value when we eval. We only delay this lookup when we are quoting the entire structure:

    '(cos arg)
    => (COS . (ARG . NIL))

There is a nice way to resolve this (i.e. to avoid getting an error from the `cons` form, and thus potentially eliminate the need for a `'` syntax) without interpreting symbols differently depending on whether they're mapped to a value or a procedure &mdash; we *always* represent procedures as data in our code. That is, the symbol `cos` above is represented by the S-expression data that was mapped to that symbol.

Since we plan to bind names to function implementations via assigning lambdas/blocks (not sure of name yet) to variables, this will work smoothly for all user-defined functions, and we only need a small hack for built-in functions to say that they work the same whether called from a symbol binding or a data representation (which are equivalent for non-built-in functions.)

For clarity we will give an example.

For a user defined function `foo`, we can call it like this:

    (foo 5)
    => result of calling foo with one argument, 5.

and when we quote it we get:

    '(foo 5)
    => (FOO . (5 . NIL))

which means we re-evaluate the meaning of `foo` in the context in which we `eval` it.

However, the third form with `cons`:

    (cons foo (cons 5 nil))
    => ((lambda foo-implementation) . (5 . NIL))

which is valid code for eval, and stores the literal implementation of `foo` from the context in which it was defined.

There is one final piece of the puzzle before we can eliminate `'` altogether from our syntax; we need a way of quoting an individual symbol so that it can be substituted for its value later, i.e. we need to be able to evaluate `foo` at the time of `eval` rather than at the time of defining the code structure. This can be done using a simple function called `symbol` that takes either a symbol or a string and returns the symbol representation (or throws an error if the string contains invalid characters):

    (symbol foo)
    => FOO
    (cons (symbol foo) (cons 5 nil))
    => (FOO . (5 . NIL))
    (cons (symbol "foo") (cons 5 nil))
    => (FOO . (5 . NIL))

So, we have eliminated the formal need for `'` in lisp. Is this A Good Idea? This language is not designed to be easy to write by hand, so the fact that

    '(foo 5)

must be written as

    (cons (symbol foo) (cons 5 nil))

is not necessarily a problem simply because it is too verbose. However, it should be noted that it may be slower, since it cannot be deduced by the parser and must be run through the interpreter before it is finished, which would be an important disadvantage. Eliminating handling of single quotes from the parser may be a significant speed gain, since it reduces the state required and a number of `if` branches, though
