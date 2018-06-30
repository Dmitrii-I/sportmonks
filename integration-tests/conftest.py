""" This is a special pytest module used during test startup to configure fixtures. """

import pytest
from sportmonks.soccer import SoccerApiV2


def pytest_addoption(parser):
    parser.addoption("--sportmonks-api-key", action="store", default="type1", help="Provide SportMonks API key")


@pytest.fixture(scope='module')
def soccer_api(request):
    return SoccerApiV2(api_token=request.config.getoption("--sportmonks-api-key"))
