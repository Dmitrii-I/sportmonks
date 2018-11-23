# Releasing

This document describes how to release `sportmonks`.

* Decide on the version according to [semantic versioning](https://semver.org).
* Put the release notes into `CHANGELOG.md` file. The release notes should describe what interesting to package users. For example, improved tests is not interesting, but new function parameter is.
* Tag the release, e.g. `git tag -a 1.0.0 -m "Release 1.0.0"`
* Upload to PyPi: `python3 setup.py upload`
    * requires [`twine`](https://pypi.org/project/twine) and PyPi credentials in `.pypirc`
* Login to [Read the Docs](https://readthedocs.org/projects/sportmonks/) and build the documentation for the new tag.
    * The new tag may not be visible at first in Read the Docs. Building the latest documentation will reveal the new tag.

