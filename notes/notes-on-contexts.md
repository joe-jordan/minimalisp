## Contexts

At the moment, Minimalisp runs all functions in the context they are called from (or rather, in a child of it). This means one can write functions which adapt to their environment, but also means unexpected coincidences and bugs may occur; particularly when a functions arguments have the same symbol bindings as things in the outer scope.

An interesting idea proposes itself, which would make closures (access to variables in the containing scope of the definition) work without much extra effort in the implementation, and would also solve this problem with context-specific functions.

If language-defined functions were to store the context in which they were defined, and to always use this parent context when called, this would make it much easier to write reliable code. It wouldn't result in more complex code, since the linked list implementation in Python readily becomes a tree with no extra cost.

We would still have the ability to use context-specific functions via storing the function body as lists and then calling `EVAL`.

