```
Help on package libyare:

NAME
    libyare - LIBrary for YARE (Yet Another Regular Expression) pattern matching

DESCRIPTION
    CONTENTS

        • 1. Usage
        • 2. Simple Patterns
        • 3. Compound Patterns
        • 4. History

    1. USAGE

    LIBYARE  implements  YARE  (Yet Another Regular Expression). YARE is a
    regular  expression format aimed to be more readable (even at the cost
    of  being  less  powerful)  than  standard regular expressions. It can
    accept  simple  patterns  (standard  Unix shell patterns) and compound
    patterns  (obtained  by  combining together simple patterns by logical
    operators and parenthesis).

    In  order  to  use  YAWP  in  your  PyPI  project,  link  it  in  your
    pyproject.toml file:

        ...
        [project]
        ...
        dependencies = ["libyare", ...]
        ...

    Then in your program you can write:

        ...
        from libyare import *
        ...
        if yarecsmatch(string, pattern): # case-sensitive match
        ...
        if yarecimatch(string, pattern): # case-insensitive match
        ...
        if yareosmatch(string, pattern): # system-depending match,
                                         # case-insensitive on MS-Windows,
                                         # else case-sensitive
        ...

    A YARE pattern can be:

        • a "simple pattern", a classic Unix shell style pattern:
            • '*' matches everything
            • '?' matches any single character
            • '[seq]' matches any single character in seq
            • '[!seq]' matches any single character not in seq
        • a "compound pattern", made by combining simple patterns by:
            • '^' not logical operator
            • '&' and logical operator
            • ',' or logical operator
            • '(' and ')' parenthesis

    2. SIMPLE PATTERNS

    Some examples of simple patterns:

        • pattern '*' matches any string
        • pattern 'abc*' matches any string starting with 'abc'
        • pattern '*abc' matches any string ending with 'abc'
        • pattern '*abc*' matches any string containing 'abc'
        • pattern '?' matches any single character
        • pattern '[az]' matches 'a' or 'z'
        • pattern '[!az]' matches any single character except 'a' or 'z'
        • pattern '[a-z]' matches any single character between 'a' and 'z'
        • pattern '[!a-z]' matches any single char not between 'a' and 'z'
        • pattern  '[a-z0-9_]' matches any single char between 'a' and 'z'
          or between '0' and '9' or equal to '_'
        • pattern '[!a-z0-9_]' matches any single char not between 'a' and
          'z' and not between '0' and '9' and not equal to '_'

    If  a  metacharacter  must  belong to a simple pattern then it must be
    quoted by '[' and ']', more exactly:

        • '*' '?' '[' '^' '&' ',' '(' and ')' must always be quoted
        • '!'  and  '-' if not between '[' and ']' have no special meaning
          and don't need to be quoted
        • ']'  only  can't be quoted, but you shouldn't need it because an
          unmatched  ']' has no special meaning and doesn't raise a syntax
          error, while unmatched '[' '(' and ')' do

    Examples:

        • pattern  '[(]*[)]'  matches  any  string  starting  with '(' and
          ending with ')'
        • pattern  '[[]*]' matches any string starting with '[' and ending
          with ']'

    You can quote metacharacter '!' too, but not immediately after '['.

        • pattern '[?!]' matches '?' and '!' only
        • pattern '[!?]' matches any character except '?'

    You can quote metacharacter '-' too, a '-' after '[' or before ']' has
    no special meaning:

        • patterns '[-pr]' and '[pr-]' matches '-' 'p' and 'r'
        • pattern '[p-r]' matches 'p' 'q' and 'r'

    '-' stands for itself even after a character interval:

        • pattern '[p-rx]' matches 'p' 'q' 'r' and 'x'
        • pattern '[p-r-x]' matches 'p' 'q' 'r' '-' and 'x'
        • pattern '[p-rx-z]' matches 'p' 'q' 'r' 'x' 'y' and 'z'
        • pattern '[p-r-x-z]' matches 'p' 'q' 'r' '-' 'x' 'y' and 'z'

    Descending character intervals do not work:

        • pattern '[z-z]' is accepted and is equivalent to '[z]'
        • pattern '[z-a]' is accepted but it does not match anything

    They  are  only  two differences between patterns defined by fnmatch()
    and  fnmatchcase()  functions  in  Python3 fnmatch module and patterns
    accepted by YARE:

        • unmatched  '['  (as  in pattern 'abc[def') is allowed by fnmatch
          but is rejected by YARE as a syntax error
        • null pattern '' is allowed by fnmatch but is rejected by YARE as
          a  syntax  error  (see  later  for  a workaround to match a null
          string by a not null pattern)

    3. COMPOUND PATTERNS

    In the following examples, p and q are two simple patterns.

    A  "compound  pattern"  is  built aggregating simple patterns by logic
    operators and parenthesis:

        • pattern '^p' matches any string not matching p
        • pattern 'p&q' matches any string matching both p and q
        • pattern 'p,q' matches any string matching p or q or both

    Examples:

        • pattern  '*.jpg,*.mp4'  matches any string ending with '.jpg' or
          with '.mp4'
        • pattern '^*' does not match anything
        • pattern '?*' matches any string of one or more characters, so...
        • pattern '^?*' matches the null string and nothing else

    Two '^' characters cancel each other out:

        • patterns '^^p' and 'p' are equivalent

    Precedence is of course '^' > '&' > ',', example:

        • pattern  '??,^s*&*t'  matches  any 2-chars string, or any string
          not starting with 's' and ending with 't'

    Precedence  can  be forced by parenthesis '(' and ')', so for instance
    the De Morgan's laws tell us that:

        • patterns '^p&^q' and '^(p,q)' are equivalent
        • patterns '^p,^q' and '^(p&q)' are equivalent

    4. HISTORY

        • 1.0.0 (Production/Stable)
            • incompatible with previous versions
            • simplified redefined and optimized

        • 0.4.3 (Experimental/Deprecated)
            • updated: documentation

        • 0.4.2 (Experimental/Deprecated)
            • updated: documentation

        • 0.4.1 (Experimental/Deprecated)
            • first version published on pypi.org

PACKAGE CONTENTS


FUNCTIONS
    yarecimatch(string, pattern)
        YARE case-insensitive match

    yarecsmatch(string, pattern)
        YARE case-sensitive match

    yareosmatch(string, pattern)
        YARE operating-system-dependent match, case-insensitive if platform is MS-Windows else case-sensitive

DATA
    __all__ = ['yarecsmatch', 'yarecimatch', 'yareosmatch']

VERSION
    1.0.0

FILE
    /home/xxxx/Documents/pypi/libyare/libyare/__init__.py


```
