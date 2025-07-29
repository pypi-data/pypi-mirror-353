![Tests and validation](https://github.com/andreasarne/python-examination/actions/workflows/test.yaml/badge.svg)

Examiner is a layer on top of pythons unittest framework, for more verbose and clear output when test fail. It is used in a university course to examine student in a introductionary python course.


# Added functionality

- Custom fail output based on docstring in test function.

    - Ability to override parts of it in assert calls.

- Color in text output.

- New Assert methods.

- Run only tests based on tags.

- Tips in output for common errors.

- Integration with [Sentry](https://sentry.io).

You can see working examples of it in `test/python` folder. To run it you first need to build it, run `make build`, it will copy external modules into the package into the `build` and `.dbwebb/test` folder which holds all the unittests. Execute `bash test.bash {KMOM/ASSIGNMENT}` (script located in `.dbwebb/test`) and include an argument of what folder inside `.dbwebb/test/suite.d` it should run the unittests from. The code that is tested are found inside `me`. If no argument is given it defaults to the current directory.



# Available arguments

Examiner uses the `argparse` module and has the following available arguments:
 * `-w, --what`, **required** - The absolute path to the desired folder containing the tests. It recursively looks in all folders for files matching the pattern `"test_(\w)*.py"`.
 * `-e, --extra` optional - Adds the pattern `"extra_test_(\w)*.py"` so the students can test their extra assignments.
 * `-t, --tags` optional - Takes a list of tags (separated by a comma). This filters what tests should be ran. If given it only runs cases that matches the tags.
 * `--trace` optional - Gives traceback output to assertion errors when they occur.
 * `-f, --failfast` - Stop executing tests on the first error or failure.
 * `-s, --showtags` - Show what tags are available for the tests. Won't run any tests!
 * `--exam` - Use when running test for an exam

Examiner utilize function docstrings for testcases to modify and specialize error outputs for each test.

TestCase classes need to inherit from `ExamTestCase` and naming should follow the regex `.*Test[0-9]?([A-Z].+)`. The number is used to sort execution order and the output.



# Writing a TestCase

TestCase class name and test funktion names are used in the output and need to follow the following patterns.

Class name, `Test[0-9]?([A-Z].+)\)`. Use a number after "test" if you want to have a fixed order in the output.

Function name, `test(_[a-z])?_(\w+)`. Use a letter after "test" if you want to have a fixed order in the output.

### Example

```python
class Test3Assignment3(ExamTestCase):
    def test_a_valid_isbn(self):
```

### Docstring

The docstring is used as error message when a test fails. This is to get better explanation of the purpose of the test. We can use predefined words to output expected value, the real value and what was used as argument. Colors can also be injected, read below for more info.

#### Available docstring values

These must not be in the docstring but then the output won't have any information about the call or values.

- `{arguments}`: This will be replaced with the arguments used to the function that is tested, if any.
- `{correct}`: This will be replaced with the correct value in the assert call. The row above this will automatically be colored green. Can be overwritten with custom coloring.
- `{student}`: This will be replaced with the value that was provided by the code in the assert call. The row above this will automatically be colored red. Can be overwritten with custom coloring.

"correct" and "student" can differ, if its the students answer or correct, depending on what assert method is used.


### Example

```python
class Test3Assignment3(ExamTestCase):
    """
    Each assignment has 3 testcase with multiple asserts.
    """
    def test_a_valid_isbn(self):
        """
        Tests different IBSN numbers.
        The following is used as argument:
        {arguments}
        The following value was expected to be returned:
        True
        Instead the it returned the following value:
        {student}
        """
```



### Available settings in a test function

- `@tags()` - add string as argument list to add tags to test. If test is run with `--tags` the test will only run if they match. Can also add kwarg "msg" to set output text for skipped tests.
- `self.norepr = True` - By default the `{student}` and `{correct}` value are run with the `repr()` function. However if you don't want that use this.
- In supported assert methods, you can override `The following value was expected to be returned:` and `Instead the it returned the following value:`. This is so we can tests different things in the same test and stil have relevant text. In assert method, send a list with two elements as the third argument. First element should be the text for the correct value and the second elemnt is the text for the wrong result.
- `self._argument = []` - This and `_multi_arguments` is used to supply value to `{arguments}` in the docstring. Use this if only one value used as argument.
- `self._multi_arguments = []` - If multiple arguments was used to function that is tested, add them to the list.

Don't use `self._argument` and `self._multi_arguments` in the same test function. Use one of them.

### Example

```python
class Test3Assignment3(ExamTestCase):
    """
    Each assignment has 3 testcase with multiple asserts.
    """
    @tags("isbn", "assignment3", msg="Skipping test without correct tag")
    def test_a_valid_isbn(self):
        """
        Tests different IBSN numbers.
        The following is used as argument:
        {arguments}
        |G|The following value was expected to be returned:|/RE|
        True
        Instead the it returned the following value:
        {student}
        """
        # self.norepr = True
        self._argument = "9781861972712"
        self.assertTrue(exam.validate_isbn(self._argument))
        self._argument = "9781617294136"
        self.assertTrue(exam.validate_isbn(self._argument), ["The following value is supposed to be printed", "The following was printed instead"])
```

Output:

```
Fails for Assignment3
    |Tests different IBSN numbers.
    |The following is used as argument:
    |'9781861972712'
    |The following value was expected to be returned:
    |True
    |Instead the it returned the following value:
    |False
    ----------------------------------------------------------------------
```



### Text coloring

Manual colors can be injected with `"|<color letter>|"` and reset value `"|/RE|"`. The reset color removes all color options up to that point. The module [colorama](https://pypi.org/project/colorama/) is used for coloring.

Available colors and letters are:

```
"G": Fore.GREEN,
"B": Fore.BLACK,
"R": Fore.RED,
"G": Fore.GREEN,
"Y": Fore.YELLOW,
"BL": Fore.BLUE,
"M": Fore.MAGENTA,
"C": Fore.CYAN,
"W": Fore.WHITE,
"RE": Fore.RESET,
```

Example:

```python
"""
Tests different IBSN numbers.
The following is used as argument:
{arguments}
|G|The following value was expected to be returned:|/RE|
True
Instead the it returned the following value:
{student}
"""
```



# New asserts

### assertModule

Check if a module exist and can be imported (does not import it). Can check both standard import and import from path. If `module_path` is None, method will check standard import. Otherwise it will check for module in `module_path`.

Run as `assertModule(module, module_path=None)`.

```
module - str: Name of module to import.

module_path - str: Realpath to directory where module should exist.
```



### assertAttribute

Check if an object has an attribute.

Run as `assertAttribute(object, attr)`.

```
object - Object: Object to look for attribute in.

attr - str: Name of attribute to look for.
```



### assertNotAttribute

Check if an object does not have an attribute.

Run as `assertNotAttribute(object, attr)`.

```
object - Object: Object to look for attribute in.

attr - str: Name of attribute to look for.
```



### assertNotAttribute

Check if that object does not have an attribute. Can be used to check that student does not import a specific module.

Run as `assertNotAttribute(object, attr)`.

```
object - Object: Object to look for attribute in.

attr - str: Name of attribute to look for.
```



### assertOrder

Checks if the elements in a sequence appear in the same order in another sequence that support the `index()` method. Ex. that a number of string appear in correct order in a bigger string. `["Hej", "Haha"]` and `"Hej ho Haha"` would assert.

Run as `assertOrder(order, container)`.

```
order - sequence: Sequence with elements in correct order.

container - sequence: Sequence to check correct order in using `index()`.
```



# Common errors caught

Some errors are caught and we add extra help text for them.

### StopIteration

Common error when the code contain too many `input()` calls than what the test expect. The default output is hard to understand.


# Sentry integration

Integration to [Sentry](https://sentry.io) is on by default. To disable Sentry add the flag `--sentry`. 

To send data to Sentry you need to add the flags `--sentry_url`, `--sentry_release` and `--sentry_sample_rate`.



# Development

We use [semantic versioning](https://semver.org/). Set version in `examiner/__init__.py` and update `CHANGELOG.md` with changes before creating a new tag. Only create new releases when code changes in `examiner`, changes that should be sent to the students.

When a new release is create, Actions will push the new `examiner` build automatically to the repo `dbwebb-se/python` and `dbwebb-se/oopython`.

### Flowchart of unittest execution

[unittest execution order](https://app.lucidchart.com/invitations/accept/f9604303-3cf8-4cbf-ab22-be0e64b99f49)



# TODO:
- [ ] Write more tests
- [ ] Try removing escaped newlines from output so CONTACT_ERROR_MSG is displayed correctly for all errors.
    - Identify errors where this happens.
- [ ] Remake flowchart as sequence diagram.
