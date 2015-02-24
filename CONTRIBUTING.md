# How to Contribute

Coding standards are designed to ensure that code is consistent in its implementation and execution. Below are a few guidelines that we need contributors to follow. Many of these should be common sense but they will give us a chance of keeping on top of things

---

## Stay Portable Where Possible

One of the goals of the scripts is that it be portable to any environment where Intel(R) DPDK vSwitch can run. Any submissions should abide to this principle. This means no hard coded variables specific to your environment. Assume that the user has nothing but this test suite on their board and handle that case. Make sure you handle RHEL and Debian alike. Etc. Etc.

---

## Languages

This one's easy - where possible, use Python. However, when this is not the case, `subprocess` or `pexpect` (see [`pexpect` vs. `subprocess`] for details on the two) can be used with either an executable or (as a last resort) a Bash script. This order of preference is illustrated below:

1. Python
2. Python w/ `subprocess` call to executable
3. Python w/ `subprocess` call to Bash script

---

## `pexpect` vs. `subprocess`

This testsuite makes use of two libraries, `pexpect` and `subprocess`. The former is used for automation of long running processes and those requiring some level of scripting or interaction. The latter, conversely, is used for short running processes that require no notable interaction.

Wrappers are provided for both in `utils.tasks` and these should be used as much as possible.

---

# Enforce Modularity

The framework is designed to be modular and self-testing, as described in [Design]. Maintain this modularity as much as possible by, for example, reducing unnecessary `import` statements.

---

# DRY, SOLID, YAGNI, etc.

Before you adding a new feature or making another change, ask yourself this:

* Is this change necessary right now?
* If a feature, is there no other way to do it, i.e. can it be done using some existing part of the framework?
* If a change, does the change reinforce the other principles of the framework?

If the answer to any of these questions is no, reevaluate your decision.

---

## General Coding Style

### Code

Abide by [PEP-8] for general code. Some particular points to note:

* Wrap code at 79 characters. No exceptions.
* Use only spaces - no tabs.
* While Python 2.7 is currently targeted, one should use Python 3.x styles where possible, i.e. import `print_function` from `__future__`.
* Use implicit string concatenation where possible. Don't use the escape character unless absolutely necessary.
* Be liberal in your use of whitespace to group related statements together. However, don't leave a space after the docstring and the first statement.
* Use single quotes for all string literals.

### Documentation

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

All code should be checked with the PyLint linter and PEP8 style guide checker. These can be run using tox, like so:

```bash
tox
```

Most PyLint errors should be resolved. You will need to do this manually. However, there are cases where they may not make sense (e.g. you **need** to pass `N` parameters to a function). In this case, disable the relevant case using an inline `disable` like so:

```python
# pylint: disable=[code]
```

On the other hand, **all** PEP8 errors should be resolved. Many of these can be done automatically using the `autopep8` tool:

```bash
tox -e autopep8
```

If there are still issues after this, they will need to resolved manually.

Note that it's also possible to generate documentation for the code. This can be done like so:

```bash
tox -e doc
```

---

[PEP-8]: http://legacy.python.org/dev/peps/pep-0008/
[PEP-257]: http://legacy.python.org/dev/peps/pep-0257/
[Sphinx guidelines]: https://pythonhosted.org/an_example_pypi_project/sphinx.html
[Design]: docs/design.md
