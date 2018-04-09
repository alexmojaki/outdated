import unittest
from warnings import catch_warnings
from contextlib import contextmanager
from uuid import uuid4

from outdated import check_outdated, utils, OutdatedCacheFailedWarning, warn_if_outdated, OutdatedPackageWarning, \
    OutdatedCheckFailedWarning
from outdated.utils import constantly


@contextmanager
def mock(old, new):
    name = old.__name__
    setattr(utils, name, new)
    try:
        yield
    finally:
        setattr(utils, name, old)


def fail(*_, **__):
    raise ValueError('Error message here')


def disable_cache():
    return mock(utils.cache_is_valid, constantly(False))


def fresh_cache():
    return mock(utils.get_cache_filename, constantly(uuid4().hex))


def fail_cache():
    return mock(utils.get_cache_filename, fail)


def fail_get_url():
    return mock(utils.get_url, fail)


class OutdatedTests(unittest.TestCase):
    version = '1.0.4'
    package = 'ask-so'

    @contextmanager
    def assert_warns(self, category, message):
        with catch_warnings(record=True) as w:
            yield
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, category)
            self.assertEqual(str(w[0].message), message)

    def test_basic(self):
        with disable_cache():
            self.example_check()

            self.assertEqual(check_outdated(self.package, '1.0'),
                             (True, self.version))

            self.assertEqual(check_outdated(self.package, self.version),
                             (False, self.version))

            self.assertEqual(check_outdated(self.package, self.version + '.0'),
                             (False, self.version))

    def test_caching(self):
        with fresh_cache():
            self.example_check()
            with fail_get_url():
                self.example_check()

    def test_cache_failure(self):
        with fail_cache():
            with self.assert_warns(
                    OutdatedCacheFailedWarning,
                    ('Failed to use cache while checking for outdated package:\n'
                     'Error message here\n'
                     'Set the environment variable OUTDATED_RAISE_EXCEPTION=1 for a full traceback.')):
                self.example_check()
                self.example_check()

    def example_check(self):
        self.assertEqual(check_outdated(self.package, '0.1'),
                         (True, self.version))

    def test_warn_if_outdated(self):
        with catch_warnings(record=True) as w:
            warn_if_outdated(self.package, self.version, raise_exceptions=True, background=False)
            self.assertEqual(len(w), 0)

        with self.assert_warns(OutdatedPackageWarning,
                               ('The package ask-so is out of date. '
                                'Your version is 0.1, the latest is 1.0.4.')):
            warn_if_outdated(self.package, '0.1', raise_exceptions=True, background=False)

        with disable_cache():
            with fail_get_url():
                with self.assert_warns(
                        OutdatedCheckFailedWarning,
                        ('Failed to check for latest version of ask-so:\n'
                         'Error message here\n'
                         'Set the environment variable OUTDATED_RAISE_EXCEPTION=1 for a full traceback.')):
                    warn_if_outdated(self.package, '0.1', background=False)

                with self.assertRaises(ValueError):
                    warn_if_outdated(self.package, '0.1', raise_exceptions=True, background=False)

        warn_if_outdated(self.package, self.version)

    def test_package_from_future(self):
        with self.assertRaises(ValueError):
            check_outdated(self.package, '5.0')


if __name__ == '__main__':
    unittest.main()
