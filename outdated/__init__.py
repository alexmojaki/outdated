import json
from datetime import datetime
from threading import Thread
from warnings import warn

from outdated import utils
from outdated.mywarnings import *

__version__ = '0.1.0'


def check_outdated(package, version):
    from pkg_resources import parse_version

    parsed_version = parse_version(version)
    latest = None

    with utils.cache_file(package, 'r') as f:
        content = f.read()
        if content:
            latest, cache_dt = json.loads(content)
            if not utils.cache_is_valid(cache_dt):
                latest = None

    if latest is None:
        url = 'https://pypi.python.org/pypi/%s/json' % package
        response = utils.get_url(url)
        latest = json.loads(response)['info']['version']

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
    def check():
        # noinspection PyUnusedLocal
        is_outdated = False
        with utils.exception_to_warning('check for latest version of %s' % package,
                                        OutdatedCheckFailedWarning,
                                        always_raise=raise_exceptions):
            is_outdated, latest = check_outdated(package, version)

        if is_outdated:
            warn('The package %s is out of date. Your version is %s, the latest is %s.'
                 % (package, version, latest),
                 OutdatedPackageWarning)

    if background:
        thread = Thread(target=check)
        thread.start()
    else:
        check()


warn_if_outdated('outdated', __version__)
