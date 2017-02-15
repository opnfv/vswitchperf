<!---
This work is licensed under a Creative Commons Attribution 4.0 International License.
http://creativecommons.org/licenses/by/4.0
-->

# General Coding Style

## Code

Abide by [PEP-8] for general code. Some particular points to note:

* Wrap code at 79 characters.
* Use only spaces - no tabs.
* Use implicit string concatenation where possible. Don't use the escape
  character unless absolutely necessary.
* Be liberal in your use of whitespace to group related statements together.
  However, don't leave a space after the docstring and the first statement.
* Use single quotes for all string literals.

## Documentation

Follow [PEP-257] and the [Sphinx guidelines] for documentation. In particular:

* Wrap docstrings at 72 characters.
* Use double-quotes for all docstrings.
* Write all inline comments in lower-case, except where using a name/initialism.
* Document **all** library functions/classes completely. Tests, however, only need a test case docstring.

To summarise the docstring conventions:

```python
def my_function(athing, stuff=5):
   """
   Summary line here in imperative tense.

   Longer description here...

   :param athing: Details about this paramter here
   :param stuff: Ditto

   :returns: None
   """
   pass  # code here...
```

### Validation

All code should be checked with the PyLint linter and PEP8 style guide checker.
Pylint can be run like so:

```bash
pylint <file or directory>
```

Most PyLint errors should be resolved. You will need to do this manually.
However, there are cases where they may not make sense (e.g. you **need** to
pass `N` parameters to a function). In this case, disable the relevant
case using an inline `disable` like so:

```python
# pylint: disable=[code]
```

On the other hand, all PEP8 errors should be resolved.

---

[PEP-8]: http://legacy.python.org/dev/peps/pep-0008/
[PEP-257]: http://legacy.python.org/dev/peps/pep-0257/
[Sphinx guidelines]: https://pythonhosted.org/an_example_pypi_project/sphinx.html
