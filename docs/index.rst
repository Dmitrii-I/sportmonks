.. sportmonks documentation master file, created by
   sphinx-quickstart on Mon Apr 30 22:51:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============

`sportmonks` is a Python 3.5+ package that implements `SportMonks <https://www.sportmonks.com>`__ API. While SportMonks (the company) offers data for various sports, this package implements only soccer. There are no plans to implement other sports.

Disclaimer: `sportmonks` Python package authors are not affiliated with SportMonks the company.


Examples
========


Print today's games:

.. code-block:: pycon

    >>> from sportmonks.soccer import SoccerApiV2
    >>> soccer = SoccerApiV2(api_token='My API token')

    >>> fixtures = soccer.fixtures_today(include=('localTeam', 'visitorTeam'))
    >>> for f in fixtures:
    >>>    print(f['localTeam']['name'], 'plays at home against', f['visitorTeam']['name'])

    Randers plays at home against FC Helsingør
    Celtic plays at home against Aberdeen
    Hibernian plays at home against Rangers
    Kilmarnock plays at home against Hearts
    Silkeborg plays at home against Lyngby
    Hobro plays at home against SønderjyskE
    OB plays at home against AGF
    AaB plays at home against København


Installation
============

Latest released version can be installed with: 

.. code-block:: shell

    pip install sportmonks

Latest development version can be installed with:

.. code-block:: shell
   
    git clone https://www.github.com/Dmitrii-I/sportmonks.git
    cd sportmonks
    pip install ./


Features
========

`sportmonks` features focus mainly on convenience:

- Methods return only data from the original SportMonks response, with non-data objects dropped. The result is shorter code: ``[f for f in fixtures_today()]`` instead of ``[f for f in fixtures_today()['data']]``.

- Methods return complete data even if the underlying HTTP endpoints are paginated. Fetching all pages is arguably the most common scenario. Not having to write `for` and `while` loops to fetch additional pages results in less boilerplate code. The trade-off is that all pages are fetched even when fewer suffice.


`sportmonks.soccer` reference
=============================

.. automodule:: sportmonks.soccer
    :members:
    :undoc-members:

