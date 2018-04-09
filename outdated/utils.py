import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta
from time import sleep
from warnings import warn

import functools

from outdated.mywarnings import OutdatedCacheFailedWarning


def format_date(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def cache_is_valid(cache_dt):
    return format_date(datetime.now() - timedelta(days=1)) < cache_dt


def retry(num_attempts=3, exception_class=Exception, sleeptime=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(num_attempts):
                try:
                    return func(*args, **kwargs)
                except exception_class:
                    if i == num_attempts - 1:
                        raise
                    else:
                        sleep(sleeptime)

        return wrapper

    return decorator


# noinspection PyCompatibility
@retry()
def get_url(url):
    try:
        from urllib.request import urlopen
    except ImportError:
        # noinspection PyUnresolvedReferences
        from urllib2 import urlopen

    return urlopen(url).read().decode('utf8')


@contextmanager
def cache_file(package, mode):
    f = DummyFile()

    with exception_to_warning('use cache while checking for outdated package',
                              OutdatedCacheFailedWarning):
        try:
            cache_path = os.path.join(tempfile.gettempdir(),
                                      get_cache_filename(package))
            if mode == 'w' or os.path.exists(cache_path):
                f = open(cache_path, mode)
        finally:
            with f:
                yield f


def get_cache_filename(package):
    return 'outdated_cache_' + package


@contextmanager
def exception_to_warning(description, category, always_raise=False):
    try:
        yield
    except Exception as e:
        if always_raise or os.environ.get('OUTDATED_RAISE_EXCEPTION') == '1':
            raise

        warn('Failed to %s:\n'
             '%s\n'
             'Set the environment variable OUTDATED_RAISE_EXCEPTION=1 for a full traceback.'
             % (description, e),
             category)


def constantly(x):
    return lambda *_, **__: x


class DummyFile(object):
    write = read = close = __enter__ = __exit__ = constantly('')
