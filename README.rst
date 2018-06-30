sportmonks
==========

This Python package implements the SportMonks HTTP API. SportMonks offers HTTP APIs for soccer and formula 1, with
additional sports on its roadmap. This package implements the soccer API, with plans to implement additional sports in
near future.

Example
=======

.. code-block:: pycon

    >>> from sportmonk.soccer import SoccerApiV2
    >>> soccer = SoccerApiV2(api_token='My API token')

    >>> fixtures = soccer.fixtures_today(include=('localTeam', 'visitorTeam'))
    >>> for fixture in fixtures:
    >>>    print(fixture['localTeam']['name'], 'plays at home against', fixture['visitorTeam']['name'])


Documentaton
============

Documentation is at http://sportmonks.readthedocs.io.


Installation
============

.. code-block:: bash

    pip install sportmonks

