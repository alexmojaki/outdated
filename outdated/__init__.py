import json
import re
from datetime import datetime
from threading import Thread

from outdated import utils
from outdated.mywarnings import *
from outdated.utils import warn_with_ignore

try:
    from .version import __version__
except ImportError:  # pragma: no cover
    # version.py is auto-generated with the git tag when building
    __version__ = "???"


def check_outdated(package, version, repository_url='https://pypi.python.org/pypi/%s/json'):
    """
    Given the name of a package on PyPI and a version (both strings), checks
    if the given version is the latest version of the package available.

    Returns a 2-tuple (is_outdated, latest_version) where
    is_outdated is a boolean which is True if the given version is earlier
    than the latest version, which is the string latest_version.

    Attempts to cache on disk the HTTP call it makes for 24 hours. If this
    somehow fails the exception is converted to a warning (OutdatedCacheFailedWarning)
    and the function continues normally.

    `repository_url` is a `%` style format string
    to use a different repository PyPI repository URL,
    e.g. test.pypi.org or a private repository.
    The string is formatted with the package name.
    """

    from pkg_resources import parse_version

    parsed_version = parse_version(version)
    latest = None

    with utils.cache_file(package, 'r') as f:
        content = f.read()
        if content:  # in case cache_file fails and so f is a dummy file
            latest, cache_dt = json.loads(content)
            if not utils.cache_is_valid(cache_dt):
                latest = None

    def get_latest():
        url = repository_url % package
        response = utils.get_url(url)
        return json.loads(response)['info']['version']

    if latest is None:
        latest = get_latest()

    parsed_latest = parse_version(latest)

    if parsed_version > parsed_latest:

        # Probably a stale cached value
        latest = get_latest()
        parsed_latest = parse_version(latest)

        if parsed_version > parsed_latest:
            raise ValueError('Version %s is greater than the latest version on PyPI: %s' %
                             (version, latest))

    is_latest = parsed_version == parsed_latest
    assert is_latest or parsed_version < parsed_latest

    with utils.cache_file(package, 'w') as f:
        data = [latest, utils.format_date(datetime.now())]
        json.dump(data, f)

    return not is_latest, latest


def warn_if_outdated(package,
                     version,
                     raise_exceptions=False,
                     background=True,
                     ):
    """
    Higher level convenience function using check_outdated.

    The package and version arguments are the same.

    If the package is outdated, a warning (OutdatedPackageWarning) will
    be emitted.

    Any exception in check_outdated will be converted to a warning (OutdatedCheckFailedWarning)
    unless raise_exceptions if True.

    If background is True (the default), the check will run in
    a background thread so this function will return immediately.
    In this case if an exception is raised and raise_exceptions if True
    the traceback will be printed to stderr but the program will not be
    interrupted.

    This function doesn't return anything.
    """

    def check():
        # noinspection PyUnusedLocal
        is_outdated = False
        with utils.exception_to_warning('check for latest version of package',
                                        OutdatedCheckFailedWarning,
                                        always_raise=raise_exceptions):
            is_outdated, latest = check_outdated(package, version)

        if is_outdated:
            warn_with_ignore(
                'The package %s is out of date. Your version is %s, the latest is %s.'
                % (package, version, latest),
                OutdatedPackageWarning,
            )

    if background:
        thread = Thread(target=check)
        thread.start()
    else:
        check()


if re.match(r"^[\d.]+$", __version__):
    warn_if_outdated('outdated', __version__)
