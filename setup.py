import os
import re

from setuptools import setup

package = 'outdated'

# __version__ is defined inside the package, but we can't import
# it because it imports dependencies which may not be installed yet,
# so we extract it manually
init_path = os.path.join(os.path.dirname(__file__),
                         package,
                         '__init__.py')
with open(init_path) as f:
    contents = f.read()
__version__ = re.search(r"__version__ = '([.\d]+)'", contents).group(1)

setup(name=package,
      version=__version__,
      description='Check if a version of a PyPI package is outdated',
      url='https://github.com/alexmojaki/' + package,
      author='Alex Hall',
      author_email='alex.mojaki@gmail.com',
      license='MIT',
      packages=[package],
      install_requires=['littleutils'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      zip_safe=False)
