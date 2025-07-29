## Testing - pytest

Write and run tests with pytest.

Django includes its own test runner and [unittest](https://docs.python.org/3/library/unittest.html#module-unittest) classes.
But a lot of people (myself included) prefer [pytest](https://docs.pytest.org/en/latest/contents.html).

In Plain I've removed the Django test runner and a lot of the implications that come with it.
There are a few utilities that remain to make testing easier,
and `plain test` is a wrapper around `pytest`.

## Usage

To run your tests with pytest, use the `plain test` command:

```bash
plain test
```

This will execute all your tests using pytest.
