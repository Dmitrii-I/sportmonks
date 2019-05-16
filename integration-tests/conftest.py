"""Configure pytest before running integration tests."""

import pytest
from sportmonks_v2.soccer import SoccerApiV2


def pytest_addoption(parser):
    """Add option to pass SportMonks API key."""
    parser.addoption("--sportmonks_v2-api-key", action="store", default="type1", help="Provide SportMonks API key")


@pytest.fixture(scope='module')
def soccer_api(request):
    """Return an instance of `SoccerApiV2`."""
    return SoccerApiV2(api_token=request.config.getoption("--sportmonks_v2-api-key"))
