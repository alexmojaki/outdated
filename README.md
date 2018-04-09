# outdated

This is a mini-library which, given a package name and a version, checks if it's the latest version available on PyPI.

To install:

    pip install outdated

## Quickstart:

    warn_if_outdated('my-package-name', '1.2.3')

This will:

- Show a warning if the given version is not the latest. The warning includes the package name, the given version, and the latest version.
- Perform the check in a background daemon thread (so it doesn't delay anything)
- Make at most one HTTP call (unless there is an HTTP error, in which case it will try 3 times) to the PyPI server for that specific package
- Cache the result of the HTTP call on disk for 24 hours
- Show a warning if any exception occurs during the check

This will *not* check what version is currently installed, it will only use the given version. Library authors must make sure that the version in their `setup.py` matches the version here.

The package name argument must be exactly the name used on PyPI, so that e.g. https://pypi.python.org/pypi/my-package-name is a valid URL.

Optional arguments:

- `background` (default `True`): run the check in a separate thread. Set to `False` to run immediately.
- `daemon` (default: `True`): if `background` is `True`, make the thread daemonic. This means that when the overall process ends, the check will stop if it hasn't completed. Has no effect if `background` is `False`.
- `raise_exceptions` (default: `False`): if `True`, allow exceptions to bubble to the top. Otherwise, show a warning including the exception message. If `background` is `True` and this is `True` then this will result in a full traceback showing but the process continuing.

## Lower level API

    is_outdated, latest_version = check_outdated('my-package-name', '1.2.3')
    
`is_outdated` is a boolean which is True if the given version is earlier than the latest version, which is the string `latest_version`.

This still makes the HTTP call with retries and caches the result on disk. It doesn't use a separate thread or emit any warnings (unless there is an exception specifically while using the cache, in which case the check will be done without the cache).

## Additional configuration

To always raise exceptions instead of converting them to warnings (both in general in `warn_if_outdated` and more specifically when there's a caching problem) set the environment variable `OUTDATED_RAISE_EXCEPTION=1`.

The warnings are also categorised so that you can easily control them with standard [warning filters](https://docs.python.org/3/library/warnings.html#the-warnings-filter). The classes are [here](https://github.com/alexmojaki/outdated/blob/master/outdated/mywarnings.py) and can be imported directly from the `outdated` module.
