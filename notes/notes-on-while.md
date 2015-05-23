It is possible to implement `while` using `eval` and `if`, if we have access to a version of `with`
which leaves us in the outer context (perhaps `without`). Whether this is a sensible objective is
questionable, as it allows users to define functions with side effects.
