sportmonks
==========

.. image:: https://api.travis-ci.org/Dmitrii-I/sportmonks.svg?branch=master
       :target: https://travis-ci.org/Dmitrii-I/sportmonks


.. image:: https://badge.fury.io/py/sportmonks.svg
       :target: https://badge.fury.io/py/sportmonks

.. image:: https://readthedocs.org/projects/sportmonks/badge
   :target: https://sportmonks.readthedocs.io

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

Documentation is at http://sportmonks.readthedocs.io

Notes
=====

If you want to redact the API-token completely in the logging, you need to make some changes to urllib3.
You need to change lines in `connectionpool.py`. Replace the lines in _make_request (line 320):

.. code-block:: pycon

    log.debug("%s://%s:%s \"%s %s %s\" %s %s", self.scheme, self.host, self.port,
          method, url, http_version, httplib_response.status,
          httplib_response.length)

with:
.. code-block:: pycon

    redacted_url = re.sub(r"(api_token=).*(&)", r"\1API_TOKEN_REDACTED\2", url)

    log.debug("%s://%s:%s \"%s %s %s\" %s %s", self.scheme, self.host, self.port,
              method, redacted_url, http_version, httplib_response.status,
              httplib_response.length)
