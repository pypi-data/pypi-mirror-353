Incoming command-line arguments are expanded using a template pattern.
Workloads often have a common form and only a small part of the shell command
need be different.

Braces, ``{}``, are used in all cases. Empty braces will substitute the full
incoming argument line. Use one of the below patterns as a shorthand notation
for many common scenarios.

The ``-t``/``--template`` argument is used by the ``client`` command to expand
templates just prior to execution. The ``cluster`` command simply forwards this
argument to all clients.

In some situations it may be useful to expand a template with the ``submit`` command.
These are expanded `prior` to scheduling as the actual `args` for the task.

Filepath Operations
^^^^^^^^^^^^^^^^^^^

Shell commands often operate on filepaths. In such cases, it may be useful to manipulate
these paths. Instead of using a shell interpolation (see below), use one of the available
shorthand notations listed here.

``{.}``
    Expand to immediate parent directory of given file.
    E.g., ``/some/path/to/file.h5`` translates to ``/some/path/to``.

``{..}``
    Expand to second parent directory of given file.
    E.g., ``/some/path/to/file.h5`` translates to ``/some/path``.

``{/}``
    The basename of the given file.
    E.g., ``/some/path/to/file.h5`` translates to ``file.h5``.

``{/-}``
    The basename of the given file without its file type extension.
    E.g., ``/some/path/to/file.h5`` translates to ``file``.

``{-}``
    The full path of the given file without the extension.
    This is useful for targeting adjacent files with a different extension.
    E.g., ``/some/path/to/file.h5`` translates to ``/some/path/to/file``.

``{+}``
    The file type extension for the given file.
    E.g., ``/some/path/to/file.h5`` translates to ``.h5``.

``{++}``
    The file type extension for the given file without the leading dot.
    E.g., ``/some/path/to/file.h5`` translates to ``h5``.

Argument Slicing
^^^^^^^^^^^^^^^^

Command-line inputs are understood as individual arguments delimited by whitespace.
Slice into the argument vector using the ``{[]}`` notation. Arguments follow zero-based
indexing. Negative index values are counting backwards from the end.

Select with a singular value.

``{[0]}``
    The first argument.

``{[1]}``
    The second argument.

``{[-1]}``
    The last argument.

Select a range with a `start` and `stop` value, non-inclusive of the `stop` value.
Including a leading or trailing colon implies the default value (inclusive).

``{[1:3]}``
    The second and third argument.

``{[:4]}``
    The first four arguments.

``{[-2:]}``
    The last two arguments.

Include a third value as a `step` (or sometimes referred to as `stride`).
Leaving out the `start` and `step` value implies starting from the first element (inclusive).

``{[::2]}``
    Every second argument starting from the first.

``{[1::2]}``
    Every odd argument.

Shell Expansion
^^^^^^^^^^^^^^^

General purpose shell commands can be expanded with the ``{% %}`` notation.
The incoming command-line args can be substituted with an ``@``.

``{% basename @ %}``
    Equivalent to ``{/}``.

``{% mktemp -d %}``
    Create temporary directory and insert its path.

Lambda Expressions
^^^^^^^^^^^^^^^^^^

Arbitrary Python expressions can be expanded with the ``{= =}`` notation.
The input argument can be used within the expression with the variable ``x``.

Exposed standard library modules include ``os``, ``os.path`` as ``path``,
``math`` and ``datetime`` as ``dt``.

Incoming arguments are intelligently coerced into the expected type.
E.g., ``2`` will be an integer, ``4.67`` a float, ``null`` and ``none``
will be a Python ``None``, and ``true``/``false`` will be the appropriate
boolean value.

``{= x * math.pi =}``
    Multiply the incoming argument (expected to be a float) by Pi.

``{= dt.datetime.fromtimestamp(x) =}``
    Convert incoming POSIX timestamp to ISO format.
