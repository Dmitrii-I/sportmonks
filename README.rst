sportmonks
==========

.. image:: https://github.com/Dmitrii-I/sportmonks/workflows/tests/badge.svg
       :target: https://github.com/Dmitrii-I/sportmonks/actions?query=workflow%3Atests


.. image:: https://badge.fury.io/py/sportmonks.svg
       :target: https://badge.fury.io/py/sportmonks


.. image:: https://readthedocs.org/projects/sportmonks/badge/?version=1.1.0
   :target: https://sportmonks.readthedocs.io/en/1.1.0/?badge=1.1.0



`sportmonks` is a Python 3.5+ package that implements `SportMonks <https://www.sportmonks.com>`__ API. While SportMonks (the company) offers data for various sports, this package implements only soccer. There are no plans to implement other sports.

Disclaimer: `sportmonks` Python package authors are not affiliated with SportMonks the company.


Examples
========


Print today's games:

.. code-block:: pycon

    >>> from sportmonks.soccer import SoccerApiV2
    >>> soccer = SoccerApiV2(api_token='My API token')

    >>> fixtures = soccer.fixtures_today(includes=('localTeam', 'visitorTeam'))
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

Documentation
=============

Documentation is at http://sportmonks.readthedocs.io.

