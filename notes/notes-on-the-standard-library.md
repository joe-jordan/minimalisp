Notes on the standard library

*this note is rather old. function names have changed somewhat, in particular `define` became `with` and `set` became `bind`. What are referred to as "blocks" have been named "contexts" inside the implementation. Some ideas in this document, particularly: `unset` (`unbind`); `split` as the inverse to `cat` (`.`); and `read` and `write` (specifically for S expressions) are good ideas that are yet to be incorporated into the implementation.*

The functions I propose implementing will be only those that are impossible to implement in the language itself.

Thus, the following symbols start in every program assigned to particular function implementations (they, as all symbols, can be renamed and overwritten at runtime - the author emphasises that there are *no magic functions* and *no macros* in minimalisp.):

Control Flow:

`define` -> defines a function implementation, and assigns that to a symbol. precise syntax TBC.
`set` -> links a symbol to a value. precise syntax also TBC.
`if` -> logical test for NIL/false/empty list, with if and else branch support.
`eval` -> run the S-expression structure as code.

Note that lambdas are trivially implementable in this form, i.e. you can quote your code, to store it as data, and then eval the data later to get the code back. However, this papers over a useful feature of Lisp lambdas (and anonymous functions in other languages) in that they are also *closures* - they encapsulate the local symbol bindings/context and use that when they execute, rather than the context in which they're being executed. Another similar concept is continuations, where entire interpreter state can be paused and restarted. Neither closures nor continuations will feature in minimalisp initially, since they will require at least some further function in this list that can manipulate the interpreter state directly. They may, however, be added in a future iteration of the language, especially if a neat abstraction can be designed that allows both features to be implemented by users as required.

possible further control flow functions:
`unset` -> unmaps a name from its current value.
`let` -> in fact, I think something `let`-flavoured can be built using `unset` - a set of statements that are "wrapped" in some `set` and `unset` calls over a list.

note on function scope:
must be careful here. values leaking out of function calls would be double plus ungood since it would prevent any meaningful abstraction and reasoning about the code - we need a concept of blocks, where local variables mask outer ones and the masks are removed at the end of the block. This may be trivial if we allow in-language storing and restoring of the interpreter state - i.e. we may need that feature in minimalisp version 1 after all, if we are to implement `define` at all.

in fact, there should logically follow a function called `block`, which executes code inside a sandbox, and returns the last value from the sandbox, throwing away all interpreter state changes - this should be enough to make functions work without an explicit `define`, we can just use a `set` and a `block` (this also gives us anonymous functions, since that's all we're `set`ing.) We can then, optionally and possibly in a later version, add some "grab interpreter state snapshot" function, and a similar "restore snapshot" function, which would allow us to build continuations (and with them, closures.)

Pair Structuring:

`car` -> retrieve the first item in a pair.
`cdr` -> retrieve the second item in a pair (the rest of the list in an S-expression).
`cons` -> construct a new pair.

(These definitions are exactly the same as in other lisps.)

note on `cons` as a replacement for `'`:
in other lisps, `'(cos 2)` is not the same as `(cons cos (cons 2 nil))` - in the latter, `cos` evaluates to a procedure object instead of a symbol. The equivalent expression is `(cons 'cos (cons 2 nil))`, often with `nil` written as `'()`, by the way. This means that it is impossible to replace the `'` functionality purely in terms of `cons` calls, since symbols do not evaluate to themselves, but to their values in the resultant expressions.

String manipulation:

`print` -> prints the arguments to stdout. If the argument is a single string, it prints the contents of the string, otherwise it prints the literal pair structures.
`cat` -> concatenates two or more strings.
`split` -> returns a list of strings, split lexically on the character provided, or split into two at the index provided.

(getting individual characters, if needed, can be implemented using splits.)

Number manipulation:

`+` -> adds two or more numeric types.
`-` -> subtracts one or more numeric types from one.
`*` -> multiplies two or more numeric types.
`/` -> performs the default numerical division operation (i.e. if everything an integer then integer division, else real division) on one numeric type using one or more other numeric types.
`/real` -> forces real division, even if arguments are integers.

(note, modulo is not included since it can be defined purely in terms of the other operators, i.e. `(% a b)` == `(- a (* (/ a b) b))`.)

TO BE ADDED:

functions for loading and saving pair structures/S-expressions to and from text files, possibly `read` and `write`, and functions for reading in text files as strings.
